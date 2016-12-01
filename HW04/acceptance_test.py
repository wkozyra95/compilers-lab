#!/usr/bin/env python
import filecmp
import unittest
import os

class AcceptanceTests(unittest.TestCase):

    @classmethod
    def add_test(cls, dirpath, filename):
        basename = os.path.splitext(filename)[0]

        dirname = os.path.join(*os.path.split(dirpath)[1:])
        name = os.path.join(dirname, basename)

        def file2func_name(filename):
            return 'test_' + filename

        def test_func(self):
            os.system("python main.py tests/{0} > tests/{1}.actual".format(filename,name))
            res = filecmp.cmp("tests/{0}.actual".format(name), "tests/{0}.expected".format(name))
            self.assertTrue(res, "files {0}.actual and {0}.expected differ".format(name))

        func_name = file2func_name(name)
        setattr(cls, func_name, test_func)

    @classmethod
    def add_tests(cls, dir):
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                elif filename.endswith('.in'):
                    cls.add_test(dirpath,filename)

if __name__ == '__main__':
    AcceptanceTests.add_tests('tests/')
    unittest.main()
