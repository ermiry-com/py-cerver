# Debug PyCerver

## faulthandler

1. Run example using faulthandler

```
python3 -q -X faulthandler examples/http/multiple.py
```

2. Example segfault output

![Multiple Example segfault faulthandler output](./images/multiple-segfault-faulthandler.png)

## gdb

1. Run python3 using gdb

```
gdb python3
```

2. Run example inside gdb 

```
run /home/ermiry/Documents/ermiry/Projects/py-cerver/examples/http/multiple.py
```

![Multiple Example run gdb output](./images/multiple-run-gdb.png)

3. Example segfault output

![Multiple Example segfault gdb output](./images/multiple-segfault-gdb.png)
