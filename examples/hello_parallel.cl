```text
int x = 0;
chan<int> c;
parallel {
  send(c, 42);
}
```