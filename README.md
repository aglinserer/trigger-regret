This is my stupid simple trigger helper to restart autopkgttest regressions, which might fail due to flaky runners.
I got inspired by the original retry-autopkgtest-regression script, which required a manual step between the retriggering.
Manual work is not something I am cut out to do, thus I did this.

# Cookie
For this to work you have to extract the cookie from the regression test site.
I do this by triggering once and copying the cookie from the network console in the dev mode.
Then I paste the data in the following format into `~/.cache/autopkgtest.cookie` to be compatible with the original script.

The format:
```
autopkgtest.ubuntu.com	TRUE	/	TRUE	0	key	value
```

