registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_57952016 = _loads('(dp1\nVcontent\np2\nVpyramid web application\np3\nsVname\np4\nVdescription\np5\ns.')
    _attrs_57952400 = _loads('(dp1\nVid\np2\nVwrap\np3\ns.')
    _attrs_57953360 = _loads('(dp1\nVcontent\np2\nVpython web application\np3\nsVname\np4\nVkeywords\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_57952976 = _loads('(dp1\n.')
    _attrs_57951760 = _loads('(dp1\n.')
    _attrs_57953296 = _loads('(dp1\nVcontent\np2\nVtext/html;charset=UTF-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_57952080 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_57952656 = _loads('(dp1\n.')
    _attrs_57952208 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_57953232 = _loads('(dp1\n.')
    _attrs_57953168 = _loads('(dp1\nVxml:lang\np2\nVen\np3\nsVxmlns\np4\nVhttp://www.w3.org/1999/xhtml\np5\ns.')
    _attrs_57951696 = _loads('(dp1\nVhref\np2\nV/\ns.')
    _attrs_57951888 = _loads("(dp1\nVhref\np2\nV${request.static_url('pyquiz:static/favicon.ico')}\np3\nsVrel\np4\nVshortcut icon\np5\ns.")
    _attrs_57952592 = _loads('(dp1\nVclass\np2\nVmiddle align-center\np3\ns.')
    _attrs_57952848 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_57952272 = _loads('(dp1\n.')
    _attrs_57953040 = _loads('(dp1\nVid\np2\nVmiddle\np3\ns.')
    _attrs_57953104 = _loads('(dp1\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u'_init_stream()'
        (_out, _write, ) = _init_stream()
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        attrs = _attrs_57953168
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
        attrs = _attrs_57953232
        _write(u'<head>\n  ')
        attrs = _attrs_57953104
        _write(u'<title>Pyquiz</title>\n  ')
        attrs = _attrs_57953296
        _write(u'<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />\n  ')
        attrs = _attrs_57953360
        _write(u'<meta name="keywords" content="python web application" />\n  ')
        attrs = _attrs_57952016
        _write(u'<meta name="description" content="pyramid web application" />\n  ')
        attrs = _attrs_57951888
        'join(value("request.static_url(\'pyquiz:static/favicon.ico\')"),)'
        _write(u'<link rel="shortcut icon"')
        _tmp1 = _lookup_attr(econtext['request'], 'static_url')('pyquiz:static/favicon.ico')
        if (_tmp1 is _default):
            _tmp1 = u"${request.static_url('pyquiz:static/favicon.ico')}"
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
            if ('&' in _tmp1):
                if (';' in _tmp1):
                    _tmp1 = _re_amp.sub('&amp;', _tmp1)
                else:
                    _tmp1 = _tmp1.replace('&', '&amp;')
            if ('<' in _tmp1):
                _tmp1 = _tmp1.replace('<', '&lt;')
            if ('>' in _tmp1):
                _tmp1 = _tmp1.replace('>', '&gt;')
            if ('"' in _tmp1):
                _tmp1 = _tmp1.replace('"', '&quot;')
            _write(((' href="' + _tmp1) + '"'))
        _write(u' />\n  ')
        attrs = _attrs_57952080
        u'test.name'
        _write(u'<h1>')
        _tmp1 = _lookup_attr(econtext['test'], 'name')
        _tmp = _tmp1
        if (_tmp.__class__ not in (str, unicode, int, float, )):
            try:
                _tmp = _tmp.__html__
            except:
                _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
            else:
                _tmp = _tmp()
                _write(_tmp)
                _tmp = None
        if (_tmp is not None):
            if not isinstance(_tmp, unicode):
                _tmp = str(_tmp)
            if ('&' in _tmp):
                if (';' in _tmp):
                    _tmp = _re_amp.sub('&amp;', _tmp)
                else:
                    _tmp = _tmp.replace('&', '&amp;')
            if ('<' in _tmp):
                _tmp = _tmp.replace('<', '&lt;')
            if ('>' in _tmp):
                _tmp = _tmp.replace('>', '&gt;')
            _write(_tmp)
        _write(u'</h1>\n</head>\n')
        attrs = _attrs_57952656
        _write(u'<body>\n  ')
        attrs = _attrs_57952400
        _write(u'<div id="wrap">\n\n    ')
        attrs = _attrs_57953040
        _write(u'<div id="middle">\n      ')
        attrs = _attrs_57952592
        _write(u'<div class="middle align-center">\n\n        ')
        attrs = _attrs_57952848
        _write(u'<h3>Results:</h3>\n        ')
        attrs = _attrs_57952976
        u'message'
        _write(u'<p>')
        _tmp1 = econtext['message']
        _tmp = _tmp1
        if (_tmp.__class__ not in (str, unicode, int, float, )):
            try:
                _tmp = _tmp.__html__
            except:
                _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
            else:
                _tmp = _tmp()
                _write(_tmp)
                _tmp = None
        if (_tmp is not None):
            if not isinstance(_tmp, unicode):
                _tmp = str(_tmp)
            if ('&' in _tmp):
                if (';' in _tmp):
                    _tmp = _re_amp.sub('&amp;', _tmp)
                else:
                    _tmp = _tmp.replace('&', '&amp;')
            if ('<' in _tmp):
                _tmp = _tmp.replace('<', '&lt;')
            if ('>' in _tmp):
                _tmp = _tmp.replace('>', '&gt;')
            _write(_tmp)
        _write(u'</p>\n        ')
        attrs = _attrs_57951760
        u'questions'
        _write(u'<h3>Questions:</h3>\n        ')
        _tmp1 = econtext['questions']
        question = None
        (_tmp1, _tmp2, ) = repeat.insert('question', _tmp1)
        for question in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_57952208
            _write(u'<ul>\n            ')
            attrs = _attrs_57952272
            u'question'
            _write(u'<li>')
            _tmp3 = question
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                if ('&' in _tmp):
                    if (';' in _tmp):
                        _tmp = _re_amp.sub('&amp;', _tmp)
                    else:
                        _tmp = _tmp.replace('&', '&amp;')
                if ('<' in _tmp):
                    _tmp = _tmp.replace('<', '&lt;')
                if ('>' in _tmp):
                    _tmp = _tmp.replace('>', '&gt;')
                _write(_tmp)
            _write(u'</li>\n        </ul>')
            if (_tmp2 == 0):
                break
            _write(' ')
        _write(u'\n        ')
        attrs = _attrs_57951696
        _write(u'<a href="/">return home</a>\n      </div>\n    </div>\n  </div>\n</body>\n</html>')
        return _out.getvalue()
    return render

__filename__ = '/home/jboisture/buildout/pyquiz/templates/grade.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
