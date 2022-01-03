#!/usr/bin/env python3

import datetime as dt
import vim
import os
import xml.etree.ElementTree as ET

cscope_db_dir = '/tmp/cscope_db'

def getDateTime():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _log(s):
    with open('/tmp/cscope_db/log', 'a+') as f:
        f.write('[%s] %s\n' % (getDateTime(), s))

def findCompPath(xml, component_name):
    match = './/component[@name="%s"]/..' % component_name
    repo_node = xml.find(match)
    if repo_node is None: return None
    repo_path = repo_node.get('path')
    if not repo_path: repo_path = repo_node.get('name')
    component_path = xml.find(match[:-3]).get('path')
    if component_path:
        return repo_path + '/' + component_path
    else:
        return repo_path

def getSbPath(cur_path):
    while cur_path != '/':
        if os.path.exists(cur_path + '/.repo'):
            return cur_path
        cur_path = os.path.dirname(cur_path)
    return None

def getComponentList(cur_path):
    clist = []
    hlist = []

    file_path = cur_path + '/Makefile.inc'
    if not os.path.exists(file_path): return []

    with open(file_path) as f:
        cmore = False
        hmore = False
        for l in f:
            l = l.split('#')[0].strip()
            if cmore:
                clist += l.split()
                if clist[-1] == '\\':
                    del clist[-1]
                    cmore = True
                else:
                    cmore = False
            elif hmore:
                hlist += l.split()
                if hlist[-1] == '\\':
                    del hlist[-1]
                    hmore = True
                else:
                    hmore = False
            elif l.startswith('USE_COMPONENTS'):
                clist += l.split()[2:]
                if clist[-1] == '\\':
                    del clist[-1]
                    cmore = True
                else:
                    cmore = False
            elif l.startswith('USE_HEADERS'):
                hlist += l.split()[2:]
                if hlist[-1] == '\\':
                    del hlist[-1]
                    hmore = True
                else:
                    hmore = False
    return clist + hlist

def getSbComponentPathList(sb_dir, cur_dir):
    plist = []
    xml_path = sb_dir + '/component-manifest/component-manifest.xml'
    if not os.path.exists(xml_path): return plist
    xml_root = ET.parse(xml_path).getroot()
    components = getComponentList(cur_dir)
    for c in components:
        component_path = findCompPath(xml_root, c)
        if not component_path:
            _log('failed to find path for component: %s' % c)
            continue
        path = '%s/%s/include' % (sb_dir, component_path)
        if path not in plist:
            plist += [path]
        path = '%s/%s/src' % (sb_dir, component_path)
        if path not in plist:
            plist += [path]
        path = '%s/%s/../include' % (sb_dir, component_path)
        if path not in plist:
            plist += [path]
        path = '%s/%s/../src' % (sb_dir, component_path)
        if path not in plist:
            plist += [path]
    return plist

def connectDB():
    cmd = 'cscope add %s' % cscope_db_dir
    vim.command(cmd)

def resetDB():
    cmd = 'cscope reset'
    vim.command(cmd)

def genCscopeDbFromPathList(db_dir, plist):
    plist_db_path = db_dir + '/plist'
    slist_db_path = db_dir + '/cscope.files'
    plist_db = []
    plist_db_size = 0
    plist_db_changed = False

    if not os.path.exists(path):
        os.makedirs(db_dir)
    if os.path.exists(plist_db_path):
        with open(plist_db_path, 'r') as f:
            for l in f:
                plist_db += [l.strip()]
        plist_db_size = len (plist_db)

    with open(slist_db_path, 'a') as slist_db_fp:
        for path in plist:
            if not os.path.exists(path):
                _log('Path not exists: %s' % path)
                continue
            path = os.path.abspath(path)
            if path in plist_db: continue
            plist_db += [path]
            plist_db_changed = True
            fnames = os.listdir(path)
            for fname in fnames:
                fname = '%s/%s' % (path, fname)
                if os.path.isdir(fname):
                    plist += [fname]
                    continue
                if fname.lower().endswith(('.h', '.cpp', '.hpp', '.c', '.cc', 'dts')):
                    print(fname, file=slist_db_fp)

    if plist_db_changed:
        with open(plist_db_path, 'a') as f:
            for i in range(plist_db_size, len(plist_db)):
                print(plist_db[i], file=f)

        org_dir = os.getcwd()
        os.chdir(db_dir)
        os.system('cscope -kbq')
        os.chdir(org_dir)
        resetDB()

def start():
    plist = []
    global cscope_db_dir
    cur_file = vim.eval('expand(\'%:p\')')
    cur_dir = os.path.dirname(cur_file)
    sb_dir = getSbPath(cur_dir)
    if sb_dir:
        cscope_db_dir = sb_dir + '/.cscope_db'
        plist += getSbComponentPathList(sb_dir, cur_dir) + [sb_dir + '/include']

    _log('processing file: %s' % cur_file)
    plist += [cur_dir, cur_dir + '/include', cur_dir + '/../include']
    genCscopeDbFromPathList(cscope_db_dir, plist)
