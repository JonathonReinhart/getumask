#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Usage: %s umask\n", argv[0]);
        return 1;
    }
    const char *umask_str = argv[1];

    char *endp;

    unsigned int new_umask = strtoul(umask_str, &endp, 0);
    if (endp == '\0') {
        fprintf(stderr, "Invalid umask value: \"%s\"\n", umask_str);
        return 1;
    }

    umask(new_umask);

    pause();

    return 0;
}
