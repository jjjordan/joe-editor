#include "putty.h"

#include "jwuserfuncs.h"
#include "jwcomm.h"
#include "jwglobals.h"
#include "jwutils.h"
#include "jwcolors.h"
#include "jwbentries.h"

static struct buffer_entry *buffers = NULL;

static void UpdateWindowTitle();


void jwUIProcessPacket(void *data, struct CommMessage* m)
{
	if (m->msg == COMM_EXIT)
	{
		jwShutdownBackend(data, m->arg1);
	}
	else if (m->msg == COMM_UPDATEBUFFER)
	{
		struct buffer_update bu;

		unmarshal_buffer_update(m, &bu);
		apply_buffer_updates(&buffers, &bu);
	}
	else if (m->msg == COMM_DONEBUFFERUPDATE)
	{
		UpdateWindowTitle();
	}
	else if (m->msg == COMM_CONTEXTMENU)
	{
		jwContextMenu(m->arg1);
	}
}

void jwSendFiles(HDROP hdrop, int x, int y)
{
	unsigned int count, i;
	wchar_t wpath[MAX_PATH];
	char path[MAX_PATH * 3];

	count = DragQueryFileW(hdrop, (unsigned int)(-1), wpath, MAX_PATH);
	for (i = 0; count > 0; count--, i++)
	{
		DragQueryFileW(hdrop, i, wpath, MAX_PATH);
		if (!wcstoutf8(path, wpath, MAX_PATH * 3))
		{
			jwSendComm3s(JW_SIDE_UI, COMM_DROPFILES, x, y, count, path);
		}
	}

	jwSendComm3(JW_SIDE_UI, COMM_DROPFILES, x, y, 0);
}

void jwSendJoeColor(void *colorp)
{
	struct jwcolors *colors = dupcolorscheme((struct jwcolors*)colorp);
	jwSendComm0p(JW_SIDE_UI, COMM_COLORSCHEME, colors);
}

static void UpdateWindowTitle()
{
	wchar_t nmbuf[MAX_PATH + 64];
	wchar_t path[MAX_PATH];
	struct buffer_entry *be;
	struct buffer_entry *active;
	int modified = 0;
	int activemodified = 0;
	int total = 0;

	if (!buffers)
	{
		return;
	}

	/* Start with a default */
	active = buffers;

	for (be = buffers; be; be = be->next)
	{
		if (be->flags & JOE_BUFFER_INTERNAL)
		{
			continue;
		}

		if (be->flags & JOE_BUFFER_MODIFIED)
		{
			modified++;
		}
		if (be->flags & JOE_BUFFER_SELECTED)
		{
			active = be;
			activemodified = !!(be->flags & JOE_BUFFER_MODIFIED);
		}
		total++;
	}

	wcscpy(nmbuf, L"");

	if (activemodified)
	{
		if (modified > 1)
		{
			wcscat(nmbuf, L"** ");
		}
		else
		{
			wcscat(nmbuf, L"* ");
		}
	}
	else if (modified)
	{
		wcscat(nmbuf, L"(*) ");
	}

	if (!wcslen(active->fname))
	{
		wcscat(nmbuf, L"Unnamed");
		wcscpy(path, L"");
	}
	else
	{
		wchar_t *slash;

		wcscpy(path, active->fname);
		slash = max(wcsrchr(path, L'/'), wcsrchr(path, L'\\'));
		if (slash)
		{
			*slash = 0;
			wcscat(nmbuf, ++slash);
		}
		else
		{
			wcscat(nmbuf, path);
			wcscpy(path, L"");
		}
	}

	if (total > 1)
	{
		wchar_t numbuf[12];

		wcscat(nmbuf, L" (+");
		wcscat(nmbuf, _itow(total - 1, numbuf, 10));
		wcscat(nmbuf, L")");
	}

	if (wcslen(path))
	{
		wcscat(nmbuf, L" [");
		wcscat(nmbuf, path);
		wcscat(nmbuf, L"]");
	}

	wcscat(nmbuf, L" - ");
	wcscat(nmbuf, jw_personality);

	set_title(NULL, nmbuf);
}

int jwAnyModified()
{
	return any_buffers_modified(buffers);
}

void jwUIExit()
{
	jwSendComm0(JW_SIDE_UI, COMM_EXIT);
}
