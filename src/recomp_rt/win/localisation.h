#ifndef CM0102_LOCALISATION_H
#define CM0102_LOCALISATION_H

/* Exact English source string in; Russian T2K-escaped text out while the overlay is active. */
int localisation_is_russian(void);
const char *localisation_text(const char *source);

#endif
