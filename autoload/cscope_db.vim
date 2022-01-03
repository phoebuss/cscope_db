let s:script_dir = escape(expand('<sfile>:p:h'), '\')

function! cscope_db#start()
python3 << EOF
cscope_db.start()
EOF
endfunction

function! cscope_db#enable()
python3 << EOF
import sys
import os
import vim

script_dir = vim.eval('s:script_dir')
src_dir = os.path.normpath(script_dir + '/../src')
sys.path[0:0] = [src_dir]
import cscope_db
cscope_db.start()
cscope_db.connectDB()
EOF

autocmd BufRead *.[cChH],*.cc,*.cpp,*.hpp call cscope_db#start()

nnoremap <C-\> :cs find s <C-R>=expand("<cword>")<CR><CR>
nnoremap <C-]> :cs find g <C-R>=expand("<cword>")<CR><CR>

endfunction
