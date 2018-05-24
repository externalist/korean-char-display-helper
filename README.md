# !! NOTE !! #
This is probably obsolete now because to the best of my knowledge, IDA > 7.x now properly supports all Unicode characters.

# Korean char display Helper IDAPython plugin

It's super annoying to see broken Korean strings in IDA.

![screenshot](/screenshots/screenshot1.png?raw=true)

This simple helper plugin tries to resolve this issue.


## [ Instructions ]
- If you know where the string is located at, you can place the cursor on the start of the string and press **Shift + A.** The string will be decoded to Korean and displayed on the screen

![screenshot](/screenshots/screenshot2.png?raw=true)

- Or you can let the plugin search all Korean strings in the binary for you. Press **Ctrl + Shift + F12** and a small window will pop up asking you to select an encoding. Choose one that you think is right, and the plugin will search through the whole image and collect strings that are encoded by the selected encoding. After it's done, a new custom view will popup with all the strings and the corresponding addresses in one screen.

![screenshot](/screenshots/screenshot3.png?raw=true)

- If you double click any line, the disassembler will move to the string's location. Afterwards, you can press **Shift + A** to convert the string to a more aesthetically pleasing form.

![screenshot](/screenshots/screenshot4.png?raw=true)

- The most significant feature is string search. From the new popup view, you can press **Alt + T** and use IDA's built-in string searching functionality to search Korean strings. The one feature everyone was missing when analyzing programs with hardcoded Korean strings in the binary.

![screenshot](/screenshots/screenshot5.png?raw=true)

- If you select the wrong encoding and get bogus results, you can always **Right Click -> Select Encoding"** and repeat the process.

![screenshot](/screenshots/screenshot6.png?raw=true)

- There are also menus in case you forget the shortcuts.

![screenshot](/screenshots/screenshot7.png?raw=true)
![screenshot](/screenshots/screenshot8.png?raw=true)

Happy Reversing!! :)


## Protips
- Most Korean strings are encoded in 'utf-16'
- If they're encoded in 'utf-8', IDA will natively display them
- Sometimes strings are encoded in 'euc-kr' or 'cp949'. Other encodings like 'johab' are very rarely seen


## Version History
### v1.0
- Initial release. User needs to Manually convert characters using Ctrl + R.
- Todo : Scan the whole image and auto convert all Korean characters.

### v1.1
- Added an auto search feature
- User can select which encoding to be used for auto search
- Added a custom view to collect the found strings
- Added more keyboard bindings & Menus
- Removed the result string from the comments because it was redundant


## Disclaimer
- This plugin heavily reuses code from the following repository : https://github.com/threatgrid/ce-xlate
- Props to threatgrid. :)
- Tested on IDA v.6.8. Other versions should work without issues. Seamlessly works with iPhone App binaries, and confirmed working on a couple win32 executables I tested.
- If you want to redistribute, please link to this repository
