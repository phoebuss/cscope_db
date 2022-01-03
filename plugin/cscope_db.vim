if has('vim_starting')
    autocmd VimEnter *.[cChH],*.cpp,*.hpp,*.cc,*.dts call cscope_db#enable()
endif
