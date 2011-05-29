registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_68599184 = _loads('(dp1\n.')
    _attrs_68598096 = _loads('(dp1\nVsrc\np2\nVstatic/scripts/jquery-1.4.2.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_68598928 = _loads('(dp1\n.')
    _attrs_68597904 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_68597776 = _loads('(dp1\n.')
    _attrs_68597584 = _loads('(dp1\nVid\np2\nVpublic\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_68598800 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_68598160 = _loads('(dp1\nVsrc\np2\nVstatic/scripts/deform.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_68598480 = _loads('(dp1\nVhref\np2\nVstatic/css/theme.css\np3\nsVrel\np4\nVstylesheet\np5\nsVtype\np6\nVtext/css\np7\ns.')
    _attrs_68598544 = _loads('(dp1\n.')
    _attrs_68597648 = _loads('(dp1\n.')
    _attrs_68598352 = _loads('(dp1\nVhref\np2\nVstatic/css/form.css\np3\nsVrel\np4\nVstylesheet\np5\nsVtype\np6\nVtext/css\np7\ns.')
    _attrs_68597264 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
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
        _write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        attrs = _attrs_68597264
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n')
        attrs = _attrs_68597648
        _write(u'<head>\n')
        attrs = _attrs_68597776
        _write(u'<title>\n   Pyquiz\n</title>\n<!-- Meta Tags -->\n')
        attrs = _attrs_68597904
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<!-- JavaScript -->\n')
        attrs = _attrs_68598160
        _write(u'<script type="text/javascript" src="static/scripts/deform.js"></script>\n')
        attrs = _attrs_68598096
        _write(u'<script type="text/javascript" src="static/scripts/jquery-1.4.2.min.js"></script>\n<!-- CSS -->\n')
        attrs = _attrs_68598352
        _write(u'<link rel="stylesheet" href="static/css/form.css" type="text/css" />\n')
        attrs = _attrs_68598480
        _write(u'<link rel="stylesheet" href="static/css/theme.css" type="text/css" />\n</head>\n')
        attrs = _attrs_68597584
        _write(u'<body id="public">\n  ')
        attrs = _attrs_68599184
        _write(u'<div>\n    ')
        attrs = _attrs_68598928
        _write(u'<h1>Create a Test</h1>\n    ')
        attrs = _attrs_68598544
        u"''"
        _write(u'<div />\n    ')
        _default.value = default = ''
        u'form'
        _content = econtext['form']
        u'_content'
        _tmp1 = _content
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
            _write(_tmp)
        _write(u'\n    ')
        attrs = _attrs_68598800
        _write(u'<script type="text/javascript">\n      jQuery(function() {\n         deform.load();\n         });\n    </script>\n  </div>\n</body>\n</html>')
        return _out.getvalue()
    return render

__filename__ = '/home/jboisture/buildout/pyquiz/templates/forms.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
