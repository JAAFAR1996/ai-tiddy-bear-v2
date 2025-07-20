## فحص الحزم المثبتة (Safety)
```bash
safety check
```

_Error or No results._
```


[33m[1m+===========================================================================================================================================================================================+[0m


[31m[1mDEPRECATED: [0m[33m[1mthis command (`check`) has been DEPRECATED, and will be unsupported beyond 01 June 2024.[0m


[32mWe highly encourage switching to the new [0m[32m[1m`scan`[0m[32m command which is easier to use, more powerful, and can be set up to mimic the deprecated command if required.[0m


[33m[1m+===========================================================================================================================================================================================+[0m


/mnt/c/Users/jaafa/Desktop/5555/ai-teddy/.venv/lib/python3.12/site-packages/safety/safety.py:1853: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
  import pkg_resources
+==============================================================================+

                               /$$$$$$            /$$
                              /$$__  $$          | $$
           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$
          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$
         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$
          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$
          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$
         |_______/  \_______/|__/     \_______/   \___/   \____  $$
                                                          /$$  | $$
                                                         |  $$$$$$/
  by safetycli.com                                        \______/

+==============================================================================+

 [1mREPORT[0m 

  Safety [1mv3.6.0[0m is scanning for [1mVulnerabilities[0m[1m...[0m
[1m  Scanning dependencies[0m in your [1menvironment:[0m

  -> /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/.venv/lib/python3.12/site-
  packages/setuptools/_vendor
  -> /usr/lib/python3.12
  -> /usr/lib/python312.zip
  -> /usr/lib/python3.12/lib-dynload
  -> /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/.venv/lib/python3.12/site-packages
  -> /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/.venv/bin

  Using [1mopen-source vulnerability database[0m
[1m  Found and scanned 166 packages[0m
  Timestamp [1m2025-07-19 12:38:13[0m
[1m  4[0m[1m vulnerabilities reported[0m
[1m  0[0m[1m vulnerabilities ignored[0m

+==============================================================================+
 [1mVULNERABILITIES REPORTED[0m 
+==============================================================================+

[31m-> Vulnerability found in python-jose version 3.5.0[0m
[1m   Vulnerability ID: [0m70716
[1m   Affected spec: [0m>=0
[1m   ADVISORY: [0mAffected versions of Python-jose allow attackers to
   cause a denial of service (resource consumption) during a decode via a...
[1m   CVE-2024-33664[0m
[1m   For more information about this vulnerability, visit
   [0mhttps://data.safetycli.com/v/70716/97c[0m
   To ignore this vulnerability, use PyUp vulnerability id 70716 in safety’s
   ignore command-line argument or add the ignore to your safety policy file.


[31m-> Vulnerability found in python-jose version 3.5.0[0m
[1m   Vulnerability ID: [0m70715
[1m   Affected spec: [0m>=0
[1m   ADVISORY: [0mAffected versions of Python-jose have a algorithm
   confusion vulnerability with OpenSSH ECDSA keys and other key formats....
[1m   CVE-2024-33663[0m
[1m   For more information about this vulnerability, visit
   [0mhttps://data.safetycli.com/v/70715/97c[0m
   To ignore this vulnerability, use PyUp vulnerability id 70715 in safety’s
   ignore command-line argument or add the ignore to your safety policy file.


[31m-> Vulnerability found in ecdsa version 0.19.1[0m
[1m   Vulnerability ID: [0m64459
[1m   Affected spec: [0m>=0
[1m   ADVISORY: [0mThe python-ecdsa library, which implements ECDSA
   cryptography in Python, is vulnerable to the Minerva attack...
[1m   CVE-2024-23342[0m
[1m   For more information about this vulnerability, visit
   [0mhttps://data.safetycli.com/v/64459/97c[0m
   To ignore this vulnerability, use PyUp vulnerability id 64459 in safety’s
   ignore command-line argument or add the ignore to your safety policy file.


[31m-> Vulnerability found in ecdsa version 0.19.1[0m
[1m   Vulnerability ID: [0m64396
[1m   Affected spec: [0m>=0
[1m   ADVISORY: [0mEcdsa does not protects against side-channel attacks.
   This is because Python does not provide side-channel secure primitives...
[1m   PVE-2024-64396[0m
[1m   For more information about this vulnerability, visit
   [0mhttps://data.safetycli.com/v/64396/97c[0m
   To ignore this vulnerability, use PyUp vulnerability id 64396 in safety’s
   ignore command-line argument or add the ignore to your safety policy file.


+==============================================================================+
   [32m[1mREMEDIATIONS[0m

  4 vulnerabilities were reported in 2 packages. For detailed remediation & 
  fix recommendations, upgrade to a commercial license. 

+==============================================================================+

 Scan was completed. 4 vulnerabilities were reported. 

+==============================================================================+[0m


[33m[1m+===========================================================================================================================================================================================+[0m


[31m[1mDEPRECATED: [0m[33m[1mthis command (`check`) has been DEPRECATED, and will be unsupported beyond 01 June 2024.[0m


[32mWe highly encourage switching to the new [0m[32m[1m`scan`[0m[32m command which is easier to use, more powerful, and can be set up to mimic the deprecated command if required.[0m


[33m[1m+===========================================================================================================================================================================================+[0m



```

⏱️ الوقت المستغرق: 58.06 ثانية


---

