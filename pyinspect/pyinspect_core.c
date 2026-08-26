#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

// Structure to hold fast metrics per file
typedef struct {
    char filename[256];
    long lines_of_code;
    long functions;
    long classes;
    long imports;
} FileMetrics;

// Helper function to fast-scan a single Python file
FileMetrics scan_python_file(const char *filepath) {
    FileMetrics metrics = {0};
    FILE *file = fopen(filepath, "r");
    if (!file) return metrics;

    // Extract just the filename from path
    const char *basename = strrchr(filepath, '/');
    if (basename) basename++;
    else basename = filepath;
    strncpy(metrics.filename, basename, sizeof(metrics.filename) - 1);

    char line[1024];
    while (fgets(line, sizeof(line), file)) {
        metrics.lines_of_code++;

        // Fast string heuristic matching for AST-like counters in C
        // (Trim leading spaces for accurate detection)
        char *ptr = line;
        while (*ptr == ' ' || *ptr == '\t') ptr++;

        if (strncmp(ptr, "def ", 4) == 0) {
            metrics.functions++;
        } else if (strncmp(ptr, "class ", 6) == 0) {
            metrics.classes++;
        } else if (strncmp(ptr, "import ", 7) == 0 || strncmp(ptr, "from ", 5) == 0) {
            metrics.imports++;
        }
    }

    fclose(file);
    return metrics;
}

// Python binding function: pyinspect_fast_scan(directory_path)
static PyObject* pyinspect_fast_scan(PyObject *self, PyObject *args) {
    const char *dir_path;
    if (!PyArg_ParseTuple(args, "s", &dir_path)) {
        return NULL;
    }

    DIR *dir = opendir(dir_path);
    if (!dir) {
        PyErr_SetString(PyExc_FileNotFoundError, "Could not open directory");
        return NULL;
    }

    PyObject *pList = PyList_New(0);
    struct dirent *entry;
    char fullpath[1024];

    while ((entry = readdir(dir)) != NULL) {
        // Skip hidden files and standard ignore directories
        if (entry->d_name[0] == '.') continue;
        if (strcmp(entry->d_name, "venv") == 0 || strcmp(entry->d_name, "__pycache__") == 0) continue;

        snprintf(fullpath, sizeof(fullpath), "%s/%s", dir_path, entry->d_name);

        struct stat path_stat;
        stat(fullpath, &path_stat);

        if (S_ISREG(path_stat.st_mode)) {
            // Check if it's a .py file
            char *ext = strrchr(entry->d_name, '.');
            if (ext && strcmp(ext, ".py") == 0) {
                FileMetrics m = scan_python_file(fullpath);

                // Build a Python dictionary for the file metrics
                PyObject *pDict = PyDict_New();
                PyDict_SetItemString(pDict, "file", PyUnicode_FromString(m.filename));
                PyDict_SetItemString(pDict, "lines_of_code", PyLong_FromLong(m.lines_of_code));
                PyDict_SetItemString(pDict, "functions", PyLong_FromLong(m.functions));
                PyDict_SetItemString(pDict, "classes", PyLong_FromLong(m.classes));
                PyDict_SetItemString(pDict, "imports", PyLong_FromLong(m.imports));

                PyList_Append(pList, pDict);
                Py_DECREF(pDict);
            }
        }
    }

    closedir(dir);
    return pList;
}

// Method definitions for Python integration
static PyMethodDef PyInspectMethods[] = {
    {"fast_scan", pyinspect_fast_scan, METH_VARARGS, "Blazing fast directory scanner in C"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef pyinspect_core_module = {
    PyModuleDef_HEAD_INIT,
    "pyinspect_core",
    "Blazing fast C core for PyInspect",
    -1,
    PyInspectMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_pyinspect_core(void) {
    return PyModule_Create(&pyinspect_core_module);
}
