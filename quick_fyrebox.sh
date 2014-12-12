echo "
                                                                                                
;kkkkkkkk,  okk.    dkk .kkkkkkkkkkkkc  ckkkkkkkk..WWWWWWWWWWW:   lWWWWWWWWWWWl  0WW.    KWN     
;kkl'''''.  oOk.    dkk  :kkd''''':kkl  ckkc'''''  :WMW::::0MM:   lMMO:::::OMMl  KMM.    XMW     
;kkc.....   oOk.    dkk  .kko.....;kkl  ckO:.....   NMN''''kMMo.  lMMd     dMMl  OMMx:',oWMK     
;kkkkkkkk;  oOk.    dkk  .kkkkkkkkkkkl  ckkkkkkkk.  NMMMMMMMMMMK  lMMd     dMMl   ,0MMMMMK;      
;kkc.....   oOkdddddkkk  .kko...dkkl.   ckO;.....   NMN.....'MMK  lMMd     dMMl  0MMd,.'lWMN     
;kk:        ,;;;;;;;xkk  .kkl    okkc   ckkl;;;;;   NMWllllloMMK  lMM0lllll0MMl  KMM.    XMW     
,xx;                xkd  .xxc     lkkl  :xxxxxxxx.  KXXXXXXXXXXO  cXXXXXXXXXXXc  OXX.    0XK     
                 .dkd             ckx.                                                          
                .xko               .                                                            
                 ';                                                                             
                                                                                                
"

read -p "Do you want to run the backround servers? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Unfortunately, you will not be able run quick fyrebox service
    Please run the servers separately from the Server and Cloud directories
    and run the client shell from the Client directory"
    exit 1
fi

echo "Starting the file server in the background ... "
cd Server
python server.py &
cd -

echo "Starting the key server in the background ... "
cd Cloud
python server.py &
cd -

echo "Starting fyrebox ... "
cd Client
python shell.py
cd -
