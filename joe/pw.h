/*
 *	Prompt windows
 *	Copyright
 *		(C) 1992 Joseph H. Allen
 *
 *	This file is part of JOE (Joe's Own Editor)
 */
#ifndef _JOE_PW_H
#define _JOE_PW_H 1

/* Prompt window (a BW) */

struct pw {
	int	(*pfunc) ();	/* Func which gets called when RTN is hit */
	int	(*abrt) ();	/* Func which gets called when window is aborted */
	int	(*tab) ();	/* Func which gets called when TAB is hit */
	unsigned char	*prompt;	/* Prompt string */
	int	promptlen;	/* Width of prompt string */
	int	promptofst;	/* Prompt scroll offset */
	B	*hist;		/* History buffer */
	void	*object;	/* Object */
	int	file_prompt;	/* Set if this is a file name prompt, so do ~ expansion */
	int	oldcury;
};

/* BW *wmkpw(BW *bw,char *prompt,int (*func)(),char *huh,int (*abrt)(),
             int (*tab)(),void *object);
 * Create a prompt window for the given window
 * file_prompt flags:
 *   bit 0: ~ expansion
 *   bit 1: update directory
 *   bit 2: seed with directory
 */
BW *wmkpw(W *w, unsigned char *prompt, B **history, int (*func) (), unsigned char *huh, int (*abrt) (), int (*tab) (), void *object, struct charmap *map, int file_prompt);

unsigned char *ask(W *w, unsigned char *prompt, B **history, unsigned char *huh, int (*tab)(), struct charmap *map, int file_prompt, int retrieve_last, unsigned char *preload);

int ucmplt(BW *bw, int k);

/* Function for TAB completion */

unsigned char **regsub(unsigned char **z, int len, unsigned char *s);

void cmplt_ins(BW *bw,unsigned char *line);

int cmplt_abrt(BW *bw,int x, unsigned char *line);

int cmplt_rtn(MENU *m,int x,unsigned char *line);

int simple_cmplt(BW *bw,unsigned char **list);

void setup_history(B **history);
void append_history(B *hist,unsigned char *s,int len);
void promote_history(B *hist, long line);
void set_current_dir(BW *bw, unsigned char *s,int simp);

extern int bg_prompt;
extern int nocurdir;

extern WATOM watompw;

unsigned char *get_cd(W *w);

#endif
