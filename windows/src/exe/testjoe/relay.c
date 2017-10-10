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

#include "jwcomm.h"

static DWORD WINAPI writeOut(LPVOID threadParam)
{
	char buff[EDITOR_TO_UI_IOSZ];
	int qd = (int)threadParam;

	for (;;) {
		struct CommMessage *msg = jwWaitForComm(&qd, 1, INFINITE, NULL);

		if (JWISIO(msg)) {
			size_t sz = jwReadIO(msg, buff);
			_write(1, buff, sz);
		}

		jwReleaseComm(qd, msg);
	}
}

void initRelay(void)
{
	int wd = jwCreateWake();
	int qd = jwCreateQueue(EDITOR_TO_UI_BUFSZ, wd);

	jwTapQueue(JW_TO_UI, qd);
	CreateThread(NULL, 0, writeOut, (LPVOID)qd, 0, NULL);
}
