#!/usr/bin/env python

KOREAN_CHAR_DISPLAY_HELPER_VERSION = "1.1"

# Korean String Display Helper -- by Externalist
#
# A simple helper script that attempts to display Korean strings in a readable form
# read instructions at https://bitbucket.org/externalist/korean-char-display-helper"


import idaapi, idautils, idc
from idaapi import Form, Choose2, plugin_t
from idc import GetManyBytes,Message,MakeComm,SetManualInsn


ENCODING_LIST = ['big5', 'cp932', 'cp949', 'cp950', 'euc-jisx0213', 'euc-jp', 'euc-kr', 'gb18030', 'gb2312', 'gbk', 'hz', 'iso-2022-jp', 'iso-2022-jp-1', 'iso-2022-jp-2', 'iso-2022-jp-3', 'iso-2022-kr', 'johab', 'shift-jis', 'shift-jisx0213', 'utf-16', 'utf-16be', 'utf-16le', 'utf-7', 'utf-8']

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def read_unicode_string(startea):
    CHUNKSIZE = 2048 # hopefully your string fits in here...
    STRTERM = "\x00\x00"
    ch_str = ""
    endea = -1
    chunk = None

    while chunk is None:
        CHUNKSIZE = CHUNKSIZE >> 1
        chunk = GetManyBytes(startea, CHUNKSIZE)
        if CHUNKSIZE == 0:
            print("[!] Failed to grab any bytes.")
            return (endea, ch_str)

    end_idx = chunk.find(STRTERM)
    if end_idx != -1:
        ch_str = chunk[:end_idx]
        endea = startea + end_idx
    if len(ch_str) % 2 != 0:
        ch_str += '\x00'
    ch_str += '\x00\x00'
    
    try:
        ch_str.decode('ascii')
        return None
    except UnicodeDecodeError:
        pass
    
    return ch_str

class EncodingSelectForm(Form):
    def __init__(self):
        Form.__init__(self,
r"""BUTTON YES* Select
Select Encoding

{FormChangeCb}
<Select an encoding :{cbReadonly}>
""", {        
        'cbReadonly': Form.DropdownListControl(
                        items=ENCODING_LIST,
                        readonly=True,
                        selval=19),
        'FormChangeCb': Form.FormChangeCb(self.OnFormChange)
        })

        self.Compile()

    def OnFormChange(self, fid):
        # Form initialization
        if fid == -1:
            self.SetFocusedField(self.cbReadonly)
            self.EnableField(self.cbReadonly, True)

        # Form OK pressed
        elif fid == -2:
            sel_idx = self.GetControlValue(self.cbReadonly)
            pass

        return 1

class KoreanStringsView(Choose2):
    def __init__(self):
        Choose2.__init__(self,
                         "Korean Strings",
                         [ ["Address",  10 | Choose2.CHCOL_HEX], 
                           ["Name",     50 | Choose2.CHCOL_PLAIN]
                         ],
                         flags = Choose2.CH_MULTI_EDIT)

        self.popup_names = ["Refresh"]
        self.icon = 80
        self.items = []
        self.items_data  = []
        self.encoding = None
        
        self.cmd_select_encoding = None

    def show(self):
        if self.encoding == None:
            f = EncodingSelectForm();
            ok = f.Execute()
            if ok == 1:
                self.encoding = ENCODING_LIST[f.cbReadonly.value]
                self.refreshitems()
                if self.Show() < 0: return False
            f.Free()
        else:
            self.refreshitems()
            if self.Show() < 0: return False
        
        # Add extra context menu commands
        # NOTE: Make sure you check for duplicates.
        if self.cmd_select_encoding == None:
            self.cmd_select_encoding = self.AddCommand("Select Encoding", flags = idaapi.CHOOSER_POPUP_MENU | idaapi.CHOOSER_NO_SELECTION, icon=80)
        return True
        
    def set_encoding(self, encoding):
        self.encoding = encoding
        return
        
    def refreshitems(self):
        if self.encoding == None:
            return
        
        self.items = []
        self.items_data  = []

        prev_string_start = 0
        prev_string_length = 0
        names_list = idautils.Names()
        for name_pair in names_list:
            if GetStringType(name_pair[0]) == None:
                continue
            else:
                try:
                    if name_pair[0] < prev_string_start + prev_string_length:
                        continue
                    prev_string_start = 0
                    prev_string_length = 0
                    unicode_string = read_unicode_string(name_pair[0])
                    if unicode_string == None:
                        continue
                    korean_string = unicode_string
                    #korean_string = korean_string.decode('utf-16')
                    korean_string = korean_string.decode(self.encoding)
                    korean_string = korean_string.encode('euc-kr')
                    self.items.append(["%08X" %(name_pair[0]), korean_string])
                    self.items_data.append([name_pair[0], korean_string])
                    prev_string_start = name_pair[0]
                    prev_string_length = len(unicode_string)
                except:
                    continue

    def OnCommand(self, n, cmd_id):
        if cmd_id == self.cmd_select_encoding:
            self.encoding = None
            self.show()
        return 1

    def OnClose(self):
        self.cmd_select_encoding = None
        return

    def OnSelectLine(self, n):
        idaapi.jumpto(self.items_data[n][0])

    def OnGetLine(self, n):
        return self.items[n]

    def OnGetIcon(self, n):
        if not len(self.items) > 0:
            return -1

        if self.items_data[n][1] == -1:
            return 80
        else:
            return 80

    def OnGetSize(self):
        return len(self.items)

    def OnRefresh(self, n):
        self.refreshitems()
        return n

    def OnActivate(self):
        self.refreshitems()
        

class KoreanCharHelperClass():
    def __init__(self):
        self.addmenu_item_ctxs = list()
        self.korean_strings_view = KoreanStringsView()
        
    def add_menu_item_helper(self, menupath, name, hotkey, flags, pyfunc, args):
        # add menu item and report on errors
        addmenu_item_ctx = idaapi.add_menu_item(menupath, name, hotkey, flags, pyfunc, args)
        if addmenu_item_ctx is None:
            return 1
        else:
            self.addmenu_item_ctxs.append(addmenu_item_ctx)
            return 0

    def add_menu_items(self):
        if self.add_menu_item_helper("View/Open subviews/Strings", "Korean Strings", "Ctrl-Shift-F12", 1, self.show_korean_strings_view, None): return 1
        if self.add_menu_item_helper("Edit/Strings/ASCII", "Korean String", "Shift-A", 0, self.convert_to_korean_string, None):  return 1
        return 0

    def del_menu_items(self):
        for addmenu_item_ctx in self.addmenu_item_ctxs:
            idaapi.del_menu_item(addmenu_item_ctx)

    def show_korean_strings_view(self):
        self.korean_strings_view.show()

    def convert_to_korean_string(self):
        startea = ScreenEA()
        endea, ch_str = self.get_ch_str(startea)
        if endea == -1:
            return

        self.present_inline(startea, ch_str)
        #MakeStr(startea, endea+1)
        idaapi.make_ascii_string(startea, endea+1 - startea, ASCSTR_C);
        
        return
       
    def present_message(self, ch_str):
        Message(ch_str)
        print ''
        
    def present_comment(self, addr, ch_str):
        MakeComm(addr, ch_str.encode('euc-kr'))
    
    def present_inline(self, addr, ch_str):
        SetManualInsn(addr, ch_str.encode('euc-kr'))

    def get_ch_str(self, startea):
        CHUNKSIZE = 2048 # hopefully your string fits in here...
        STRTERM = "\x00\x00"
        ch_str = ""
        endea = -1
        chunk = None

        while chunk is None:
            CHUNKSIZE = CHUNKSIZE >> 1
            chunk = GetManyBytes(startea, CHUNKSIZE)
            if CHUNKSIZE == 0:
                print("[!] Failed to grab any bytes.")
                return (endea, ch_str)

        end_idx = chunk.find(STRTERM)
        if end_idx != -1:
            ch_str = chunk[:end_idx]
            endea = startea + end_idx
        if len(ch_str) % 2 != 0:
            ch_str += '\x00'
            endea += 1
        
        foundEncodingFlag = False
        for encoding in ENCODING_LIST:
            try:
                test_str1 = ch_str.decode(encoding)
                test_str2 = test_str1.encode('euc-kr')
                foundEncodingFlag = True
                print '[ ' + encoding + ' string ] '
                self.korean_strings_view.set_encoding(encoding)
                break
            except:
                #print("[!] String does not appear to be %s encoded." % encoding)
                continue
        
        if foundEncodingFlag == False:
            endea = -1
        
        return (endea, ch_str.decode(encoding))


class korean_char_helper_t(plugin_t):
    wanted_name = "Fix broken Korean Characters"
    wanted_hotkey = ""
    comment = "A simple helper script that attempts to display Korean strings in a readable form"
    help = "Read instructions at : https://bitbucket.org/externalist/korean-char-display-helper"
    #flags = idaapi.PLUGIN_UNL;
    flags = 0

    def init(self):  
        global korean_char_helper_class

        # Check if already initialized
        if not 'korean_char_helper_class' in globals():
            korean_char_helper_class = KoreanCharHelperClass()
            if korean_char_helper_class.add_menu_items():
                print "Failed to initialize Korean char helper plugin."
                korean_char_helper_class.del_menu_items()
                del korean_char_helper_class
                return idaapi.PLUGIN_SKIP
            else:  
                print("Initialized Korean char Helper v%s" % KOREAN_CHAR_DISPLAY_HELPER_VERSION)
            
        return idaapi.PLUGIN_OK

    def run(self, arg):
        global korean_char_helper_class
        #korean_char_helper_class.show_korean_strings_view()

    def term(self):
        pass
        
        
def PLUGIN_ENTRY():
    return korean_char_helper_t()

if __name__ == '__main__':
    pass