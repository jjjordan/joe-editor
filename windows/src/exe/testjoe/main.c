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
#include <stdlib.h>
#include <stdio.h>
#include "jwglobals.h"
#include "relay.h"

int PuttyWinMain(HINSTANCE, HINSTANCE, LPSTR, int);
int jwInitJoe(int, wchar_t**);

int initTest(int relayqd);

int wmain(int argc, wchar_t *argv[])
{
	if (!jwInitJoe(argc, argv)) {
		int relayqd;

		relayqd = initRelay();
		if (relayqd >= 0 && !initTest(relayqd)) {
			char *p = getenv("JOETEST_SHOW");
			int show = p ? atoi(p) : 1;

			return PuttyWinMain(GetModuleHandleW(NULL), NULL, "", show);
		} else {
			fprintf(stderr, "Failed to initialize testing stuff\n");
			return 1;
		}
	} else {
		return 1;
	}
}

int initTest(int relayqd)
{
	struct test_params params;
	HANDLE hConsole;
	CONSOLE_SCREEN_BUFFER_INFO scrn;
	char *p;

	hConsole = CreateFile("CONOUT$", GENERIC_WRITE | GENERIC_READ, FILE_SHARE_WRITE, 0, OPEN_EXISTING, 0, 0);
	if (hConsole == INVALID_HANDLE_VALUE) {
		return 1;
	}

	GetConsoleScreenBufferInfo(hConsole, &scrn);
	params.cols = scrn.srWindow.Right - scrn.srWindow.Left + 1;
	params.rows = scrn.srWindow.Bottom - scrn.srWindow.Top + 1;
	
	p = getenv("JOETEST_PERSONALITY");
	if (p) {
		params.personality = p;
	} else {
		// Default to the standard
		params.personality = "joe";
	}

	params.home = getenv("JOETEST_HOME");
	params.data = getenv("JOETEST_DATA");
	params.term = getenv("JOETEST_TERM");
	params.relayqd = relayqd;

	return jwInitTest(&params);
}