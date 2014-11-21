
/*
** Replacement for i18n.c in the JOE source.  Windows knows the character classes
** and purportedly these functions run quicker than a manual less-than/greater-than
** approach.  More importantly, we don't need to store tables for everything.
*/

#include <wchar.h>

int joe_iswupper(void *foo, int c)
{
	return iswupper(c);
}

int joe_iswlower(void *foo, int c)
{
	return iswlower(c);
}

int joe_iswalpha(void *foo, int c)
{
	return iswalpha(c);
}

int joe_iswalpha_(void *foo, int c)
{
	return (c == 0x5F) || iswalpha(c);
}

int joe_iswalnum_(void *foo, int c)
{
	return (c == 0x5F) || iswalnum(c);
}

int joe_iswdigit(void *foo, int c)
{
	return iswdigit(c);
}

int joe_iswspace(void *foo, int c)
{
	return iswspace(c);
}

int joe_iswctrl(void *foo, int c)
{
	return iswcntrl(c);
}

int joe_iswpunct(void *foo, int c)
{
	return iswpunct(c);
}

int joe_iswgraph(void *foo, int c)
{
	return iswgraph(c);
}

int joe_iswprint(void *foo, int c)
{
	return iswprint(c);
}

int joe_iswxdigit(void *foo, int c)
{
	return iswxdigit(c);
}

int joe_iswblank(void *foo, int c)
{
	// Don't know what this maps to in Windows, so just use the
	// intervals from i18n.c

	return c >= 0x2000
		  ? ((c <= 0x200B && c != 0x2007) || c == 0x205F || c == 0x3000)
		  : (c == 0x0009 || c == 0x0020 || c == 0x1680);
}

int joe_towupper(void *foo, int c)
{
	return towupper(c);
}

int joe_towlower(void *foo, int c)
{
	return towlower(c);
}

int unictrl(int ucs)
{
	/* Control characters are one column wide in JOE */
	if (ucs < 32 || ucs == 0x7F)
		return 1;

	if (ucs >= 0x80 && ucs <= 0x9F)
		return 4;

	/* More control characters... */
	if (ucs>=0x200b && ucs<=0x206f) {
		if (ucs<=0x200f) return 6;
		if (ucs>=0x2028 && ucs<=0x202E) return 6;
		if (ucs>=0x2060 && ucs<=0x2063) return 6;
		if (ucs>=0x206a) return 6;
	}

	/* More control characters... */
	if (ucs>=0xFDD0 && ucs<=0xFDEF)
		return 6;

	if (ucs==0xFEFF)
		return 6;

	if (ucs>=0xFFF9 && ucs<=0xFFFB)
		return 6;

	if (ucs>=0xFFFE && ucs<=0xFFFF)
		return 6;

	return 0;
}

int joe_wcwidth(int wide, int ucs)
{
	/* Use common wcwidth */
	int wcwidth(int);
	int control;

	/* First check in original source was:
		// If terminal is not UTF-8 or file is not UTF-8: width is 1
	        // FIXME
		if (!locale_map->type || !wide)
			return 1;
	   But locale_map->type should be true, because we should *always* be in UTF-8 mode.
	*/

	if (!wide)
	{
		return 1;
	}

	control = unictrl(ucs);
	return control ? control : wcwidth(ucs);
}
