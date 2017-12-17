def debug(yes, *this):  # pragma: no cover
    if yes:
        if len(this) > 1:
            for x in this[:-1]:
                print(x)
        print(this[-1])


class Program(object):
    def __init__(self, parser, story):
        self.parser = parser
        parser.program = self
        self.story = story

    def _json_next(self, dct, method, parent=None):
        if isinstance(method, Method):
            dct[str(method.lineno)] = dict(
                method=method.method,
                output=method.output,
                linenum=method.lineno,
                args=self._dump_json(method.args),
                kwargs=self._dump_json(method.kwargs),
                parent=parent.lineno if parent else None
            )
            if method.suite:
                for e in method.suite:
                    self._json_next(dct, e, method)

        else:
            for m in method:
                self._json_next(dct, m, parent)

    def _dump_json(self, obj):
        if type(obj) in (type(None), bool, int, float):
            return obj
        elif hasattr(obj, 'json'):
            return obj.json()
        elif type(obj) is dict:
            return dict([(key, self._dump_json(var))
                         for key, var in obj.items()])
        else:
            return [var.json() if hasattr(var, 'json') else var
                    for var in obj]

    def json(self):
        from . import version

        dct = {}
        self._json_next(dct, self.story)
        return dict(
            version=version,
            script=dct
        )


class Method(object):
    def __init__(self, method, parser, lineno,
                 suite=None, output=None, args=None, kwargs=None):
        self.method = method
        self.parser = parser
        self.lineno = str(lineno)
        self.output = output
        self.suite = suite
        self.args = args
        self.kwargs = kwargs


class Path(object):
    def __init__(self, parser, lineno, path, agg=None):
        self.parser = parser
        self.lineno = lineno
        self.path = path
        self.agg = agg

    def add(self, path):
        self.path = '%s.%s' % (self.path, path)
        return self

    def json(self):
        if self.agg:
            return dict(path=self.path, agg=self.agg)
        else:
            return dict(path=self.path)


class String(object):
    def __init__(self, data):
        self.chunks = [data]

    def add(self, data):
        self.chunks.append(data)
        return self

    def json(self):
        is_complex = False
        for st in self.chunks:
            if isinstance(st, Path):
                is_complex = True
                break

        if is_complex:
            string = []
            values = {}
            for st in self.chunks:
                if isinstance(st, Path):
                    values[str(len(values))] = st.json()
                    string.append('{%d}' % (len(values) - 1))
                else:
                    string.append(st)
            return dict(string=''.join(string).strip(), values=values)

        else:
            return dict(value=' '.join([d.strip()
                                        for d in self.chunks]).strip())


class Expression(object):
    def __init__(self, expression):
        self.expressions = [('', expression)]

    def add(self, method, expression):
        self.expressions.append((method, expression))
        return self

    def json(self, evals=None, values=None):
        if evals is None:
            if len(self.expressions) == 1:
                e = self.expressions[0][1]
                return e.json() if hasattr(e, 'json') else e
            evals = []
            values = {}
        for mixin, expression in self.expressions:
            evals.append(mixin)

            if isinstance(expression, Expression):
                _d = expression.json(evals, values)
                evals = [_d['expression']]
                values = _d['values']

            elif hasattr(expression, 'json'):
                d = expression.json()
                i = (max(map(int, values.keys())) + 1) if values else 0
                values[str(i)] = d
                evals.append('{%d}' % (i))
            else:
                evals.append(expression)

        return dict(expression=' '.join([ev for ev in evals if ev != '']),
                    values=values)


class Comparison(object):
    def __init__(self, left, method, right):
        self.left = left
        self.method = method
        self.right = right

    def json(self):
        if hasattr(self.left, 'json'):
            _left = self.left.json()
        else:
            _left = self.left

        if hasattr(self.right, 'json'):
            _right = self.right.json()
        else:
            _right = self.right

        return dict(
            method=self.method,
            left=_left,
            right=_right
        )
