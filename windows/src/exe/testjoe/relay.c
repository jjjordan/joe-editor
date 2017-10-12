/*
 *  This file is part of Joe's Own Editor for Windows.
 *  Copyright (c) 2017 John J. Jordan.
 *
 *  Joe's Own Editor for Windows is free software: you can redistribute it 
 *  and/or modify it under the terms of the GNU General Public License as
 *  published by the Free Software Foundation, either version 2 of the 
 *  License, or (at your option) any later version.
 *
 *  Joe's Own Editor for Windows is distributed in the hope that it will
 *  be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 *  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Joe's Own Editor for Windows.  If not, see
 *  <http://www.gnu.org/licenses/>.
 */

#include "jwwin.h"
#include <io.h>
#include <stdlib.h>
#include <assert.h>

#include "jwcomm.h"

struct queues {
	int stdinqd;
	int stdoutqd;
};

static DWORD WINAPI readIn(LPVOID threadParam)
{
	struct queues *q = (struct queues *) threadParam;
	int qd = q->stdinqd;
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
	DWORD lastCount = 0;
	PINPUT_RECORD events = NULL;
	char buffer[UI_TO_EDITOR_IOSZ];

	for (;;) {
		DWORD count;
		BOOL hasKeys = FALSE;

		WaitForSingleObject(hStdin, INFINITE);

		/* Check low-level IO for window resize events. */
		GetNumberOfConsoleInputEvents(hStdin, &count);
		if (count > lastCount) {
			lastCount = count;
			if (events) {
				free(events);
			}

			events = (PINPUT_RECORD)malloc(count * sizeof(INPUT_RECORD));
		}

		if (count > 0) {
			int i;
			
			PeekConsoleInput(hStdin, events, lastCount, &count);
			for (i = 0; i < count; i++) {
				if (events[i].EventType == WINDOW_BUFFER_SIZE_EVENT) {
					CONSOLE_SCREEN_BUFFER_INFO scrn;
					char *p;

					GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &scrn);
					jwSendComm2(qd, COMM_WINRESIZE, (scrn.srWindow.Right - scrn.srWindow.Left) + 1, (scrn.srWindow.Bottom - scrn.srWindow.Top) + 1);
				} else if (events[i].EventType == KEY_EVENT) {
					hasKeys = TRUE;
				}
			}
		}

		/* Check high-level IO for data */
		if (hasKeys && ReadFile(hStdin, buffer, UI_TO_EDITOR_BUFSZ, &count, NULL) && count > 0) {
			jwWriteIO(qd, buffer, count);
		} else {
			FlushConsoleInputBuffer(hStdin);
		}
	}

	return 0;
}

static DWORD WINAPI writeOut(LPVOID threadParam)
{
	char buff[EDITOR_TO_UI_IOSZ];
	struct queues *q = (struct queues *) threadParam;
	int qd = q->stdoutqd;
	HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);

	/* Wait for rendezvous before starting thread to read stdin */
	for (;;) {
		struct CommMessage *msg = jwWaitForComm(&qd, 1, INFINITE, NULL);
		if (msg->msg == COMM_RENDEZVOUS) {
			/* Good. */
			jwReleaseComm(qd, msg);
			CreateThread(NULL, 0, readIn, (LPVOID)q, 0, NULL);
			break;
		} else if (msg->msg == COMM_EXIT) {
			return 1;
		} else {
			assert(0);
		}
	}

	for (;;) {
		struct CommMessage *msg = jwWaitForComm(&qd, 1, INFINITE, NULL);

		if (JWISIO(msg)) {
			size_t sz = jwReadIO(msg, buff);
			WriteFile(hStdout, buff, sz, NULL, NULL);
		}

		jwReleaseComm(qd, msg);
	}
}

int initRelay(void)
{
	struct queues *q = (struct queues *) malloc(sizeof(struct queues));
	HANDLE hConsole = GetStdHandle(STD_INPUT_HANDLE);
	DWORD mode;

	q->stdoutqd = jwCreateQueue(EDITOR_TO_UI_BUFSZ, jwCreateWake());
	q->stdinqd = jwCreateQueue(UI_TO_EDITOR_BUFSZ, JW_TO_UI); /* Wake the UI so it can relay the message for us. */

	jwTapQueue(JW_TO_UI, q->stdoutqd);
	CreateThread(NULL, 0, writeOut, (LPVOID)q, 0, NULL);

	/* Set up console */
	GetConsoleMode(hConsole, &mode);
	mode &= ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT);
	mode |= ENABLE_WINDOW_INPUT;
	SetConsoleMode(hConsole, mode);

	return q->stdinqd;
}
