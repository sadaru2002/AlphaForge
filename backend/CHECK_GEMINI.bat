@echo off
echo Checking Gemini AI Validation Status...
echo.

REM Create SSH key
(
echo -----BEGIN RSA PRIVATE KEY-----
echo MIIEogIBAAKCAQEA7BrG2CyvvW82CZha18shMyOsTKZZzmviwREhuQgSycjFAlCE
echo Fh/Dkulztp1mV7hUReBMg4OANBM8z+m6ljOHw/lxpnnkRATcyFBPKL42ouDLvjOa
echo HU9J+vrMpPh57XiPsypm4hb9LwOg4fc2tYIwo/RpUEmNz+cb6naBh3huy+9NnSAI
echo VEraS2YRGTOL17W2MwlnSD+eBqvsICFKlocWYp+hYM1xQsAEbayotD9kVgOqQp/v
echo DL322PJytC/l1+/+Bw4v9zTdllK5JKEMLuFkEp7wY2DnixHigokamyxZb2j72tYq
echo dlICOaCQEeP3XSg4aIGCJFqb9V55soacKpIEnwIDAQABAoIBADM/SKPJZ0fV6MPC
echo Zw1p0MX52z8z6FBOyIQhhNFVuEZGJsTu1wy6TkgIFg6wMXOe1ePo4JK3K0+iUVPL
echo pq1NeA2IiiuZT3uYFpgAHn54cwF9i5u4NZ5hBGzOnTa9nDF4NrCr5nLyjHf08Km7
echo cAuLu6UKuwUrQfW7cyq8GDdgY6Qt3U65HMYCLPsHxwYtl3R2OaAcT1q7mC7re2ro
echo Y3f3vjEYyLcjUQVA4a0pu7s4fPOgG3LRhk2Skr5KFwuhuWGjASurwsVwhcp8DxnX
echo JCW/fXaIdS0/W/KQuQlq7IfbWZM4JB5KAYOgJxiJJf58BlPjecW7VlgLPGtva2BQ
echo N9yEtlECgYEA9/efBRkePDQ6RxUgW3x4C/wWuJD79yNNt21xmHuWDZvWFqmIZ4Bj
echo H19WQrTEorCXMlekxaxqt5q37yuJYtEDRCDpLnKG54VggOLpniGFk4A1X5EfVTds
echo y4nllfE26iE0J1j3g8ggrJ1ArJOfv3DGSnAhEOR9o9sbYniYuDJojfkCgYEA88DH
echo cSItluyYgUHGGTre90BltShouea0D55Dh7L414XkczImK9oxJYTD1kLITNjSE0PP
echo 7o/fxqITeTDZiBh23uM6+MAZQIkX6W8U0FnZqQ0dI83NJhjkbTCbx9lGDR/aP2qr
echo htC3SYpyF3AMhdBPwlxqzpciu7G9y03N/2H9LVcCgYB9RpcKZlRGKkS/IMdGMS4d
echo L/Dyshz6ENX0s9BOLzHyEicpL+GAGPb7JJlZ/iXR49GfV3QhgigwNnRy2tYAHIS/
echo 6LimBKpvUY0d0IYio+DuUjmk3Jat4OCQPEzHYiRSSRAmSOZTp8oKKzA/gB2XBIzJ
echo krjB5g4ruEiviSnu9VipUQKBgGDrA+H93valeDXcuzGI8OKKnmYbfRh9nJahLOSl
echo yr+XIzCSfg7toKD0WxG0WAQGKfEzA1gtqKJIC0oinDu6znjtDKOfber1F6bfXf1B
echo 3IOVDUMRL0K4nwqzSx15TJsnURXqCe1+y4HYJGkhSjlijHQRXv5ppYvPrlFJzGCA
echo y7PdAoGATS6yFLwpobWXShSLKOAG86jXukNtAzXSR3NS2D6Kx/xmWVbK9pb4+GuU
echo Z3SaMx1tSjhoFPJHF1X3OPp2GnyzLwqznJo3GdOvQVBbvZmsVJ/PjOQFMohtOsb7
echo bsCMnKrJxojKiKS2SYIT+UcBYsJV61i2qOWr51lB51/GR/at+DQ=
echo -----END RSA PRIVATE KEY-----
) > %TEMP%\oracle.key

echo [1] Checking Gemini API Key Status:
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker exec alphaforge-backend printenv GEMINI_API_KEY | head -c 20"
echo ...

echo.
echo [2] Checking Backend Logs for Gemini Activity:
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker logs alphaforge-backend 2>&1 | grep -i gemini | tail -5"

echo.
echo [3] Checking if Gemini validation is enabled in code:
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker exec alphaforge-backend cat /app/backend/enhanced_strategy_integration.py | grep -A 5 'gemini_validation'"

del %TEMP%\oracle.key
