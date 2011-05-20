#define KEYMACROS_H "$Id: objectkeymacros.h 117967 2010-10-27 19:17:39Z jim $\n"
#define KEY_TYPE PyObject *
#define KEY_TYPE_IS_PYOBJECT
#define TEST_KEY_SET_OR(V, KEY, TARGET) if ( ( (V) = PyObject_Compare((KEY),(TARGET)) ), PyErr_Occurred() )
#define INCREF_KEY(k) Py_INCREF(k)
#define DECREF_KEY(KEY) Py_DECREF(KEY)
#define COPY_KEY(KEY, E) KEY=(E)
#define COPY_KEY_TO_OBJECT(O, K) O=(K); Py_INCREF(O)
#define COPY_KEY_FROM_ARG(TARGET, ARG, S) TARGET=(ARG)
