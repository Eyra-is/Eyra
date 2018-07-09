# Eyra

Eyra provides tools for data gathering designed to be used to make speech corpora for under-resourced languages.  

The team at Reykjavik University published an article on this software for the SLTU 2016 conference, which can be found online and in this repository at [`Docs/Petursson_et_al_2016.pdf`](https://github.com/Eyra-is/Eyra/blob/master/Docs/Petursson_et_al_2016.pdf).

## Installation

Currently, the Eyra backend has to be run on Linux. Systems we've used are mainly **Debian 8** and to a lesser degree, **Ubuntu 14.04 and 16.04**.

The recording devices themselves (phones, laptops, anything with a compatible browser) can use Chrome or Firefox. However, when using phones, we recommend using our Android app (located in [`AndroidApp`](https://github.com/Eyra-is/Eyra/blob/master/AndroidApp)). It bypasses a nasty bug we discovered where audio recorded through a phone's browser is 48kHz, but the data in it appears to be limited to 16kHz.
    
If you want Quality Control (QC) to work, you need to install Kaldi and more, look at how to set it up in [DEVELOPER.md](https://github.com/Eyra-is/Eyra/blob/master/DEVELOPER.md). 

### Laptop installation (local wifi)

Setup a laptop which the phones (recording devices) can connect to in an offline setting.

* **Backend (on the laptop)**  
    You have to initially have an internet connection and run  
    `./Setup/setup.sh --all` and then  
    `sudo service apache2 restart`

    *Warning: Running [`./Setup/setup.sh --all`](https://github.com/Eyra-is/Eyra/tree/master/Setup/setup.sh) or [`./Setup/setup.sh --ap`](https://github.com/Eyra-is/Eyra/tree/master/Setup/setup.sh) disables your wifi while setting up the access point. If this is not what you want, a way to enable the wifi is the following:*  
    * `sudo nano /etc/NetworkManager/NetworkManager.conf` -> change `managed=false` to `managed=true`
    * `sudo service network-manager restart` 
 
    *Wifi should now work again.*
    
* **Client-side (on the devices)**
    * Android app  
        1. Install [`AndroidApp/versions/v1.4/app-debug-v1.4.apk`](https://github.com/Eyra-is/Eyra/blob/master/AndroidApp/versions/v1.4/app-debug-v1.4.apk) (or whatever is the latest version) on your phone.  
        2. Install the self-signed certificate on your phone ([`Setup/src/apache/tmpl/etc_ssl_certs_rootCA.pem`](https://github.com/Eyra-is/Eyra/tree/master/Setup/src/apache/tmpl/etc_ssl_certs_rootCA.pem))
        3. Connect to FeedMeData Wifi and start the Eyra Android app.
    * Straight outta browser  
        1. Connect to FeedMeData Wifi.
        2. Navigate to https://local.eyra.is
        3. Go to `Settings->Register device` (optional)
    
    Optionally, you can go to `Settings->Set instructor` if you want to link this device to a certain field worker/instructor.

### Internet installation (e.g. for crowdsourcing)

Setup a server (we use apache).

* **Backend**  
    Run `./Setup/setup.sh --all --no-ap` and then  
    `sudo service apache2 restart`

    You might want to look at [`Setup/src/apache/tmpl/etc_apache2_sites-available_datatool.conf`](https://github.com/Eyra-is/Eyra/tree/master/Setup/src/apache/tmpl/etc_apache2_sites-available_datatool.conf) (src) or `/etc/apache2/sites-enabled/datool.conf` (generated) and e.g. adjust the parameters for the `mpm_worker_module`.  

    The laptop setup uses a self-signed certificate (which needs to be manually put on and installed on the phones), but the internet one should use a real certificate (this depends on which certificate used). We used [letsencrypt](https://letsencrypt.org/) for a free certificate. This has to be done manually.
    
    This should work on both **Debian 8 Jessie** and **Ubuntu Server 14.04**.  
    
    
* **Client-side**  
    Same as the laptop installation, except, no need to manually install the certificates and of course the link to your server depends on where you host it (you might need to change this in the Android app code (see [DEVELOPER.md](https://github.com/Eyra-is/Eyra/tree/master/DEVELOPER.md) for details)).

## Usage

Eyra is not perfect software. You can look at [issues](https://github.com/Eyra-is/Eyra/issues) on github (e.g. with label bugs) for example. If you do fix something please [contribute](https://github.com/Eyra-is/Eyra/tree/master/CONTRIBUTING.md)!

### Basic usage:

In the GUI

1. Hit begin  
2. Type your username (anything)  
3. Enter your info (gender, etc.)
4. Hit Rec to start recording and display a prompt
5. [optional] Hit Skip to skip this prompt and immediately start the next one
6. Hit Stop when you have read the prompt

See [`Docs/UserGuideInstructions.pdf`](https://github.com/Eyra-is/Eyra/tree/master/Docs/UserGuideInstructions.pdf). An example instructions on recording offline can be found at [`Docs/DataUploadingInstructions.pdf`](https://github.com/Eyra-is/Eyra/tree/master/Docs/DataUploadingInstructions.pdf).

If you require your users to give consent for their recordings to be used, you can look at an example participant agreement used at RU at [`Docs/EXAMPLE_PARTICIPANTAGREEMENT.pdf`](https://github.com/Eyra-is/Eyra/tree/master/Docs/EXAMPLE_PARTICIPANTAGREEMENT.pdf). This is only an example, and you should have your lawyers look over your own agreement.

More details about the software and its usage can be found in [DEVELOPER.md](https://github.com/Eyra-is/Eyra/tree/master/DEVELOPER.md).

## Contributing

See [`CONTRIBUTING.md`](https://github.com/Eyra-is/Eyra/tree/master/CONTRIBUTING.md). A list of contributors with contact info can be found in the  [`CONTRIBUTORS`](https://github.com/Eyra-is/Eyra/tree/master/CONTRIBUTORS) file.

## Credits

This project wouldn't have been possible without the cooperation of 

* Google

Project head:

* Jón Guðnason

Original developers at Reykjavik University:

* Matthías Pétursson  
* Róbert Kjaran  
* Simon Klüpfel  
* Sveinn Ernstsson  

Many thanks to the people at Google:

* Oddur Kjartansson  
* Linne Ha  
* Martin Jansche  
* and more  

Additional developers
* Judy Fong
* Stefán Gunnlaugur Jónsson

Technical Writer
* Judy Fong

## License

This software is licenced under the Apache Version 2.0 licence as stated in the [LICENCE](https://github.com/Eyra-is/Eyra/tree/master/LICENSE) document. Some parts of the software are licenced under the MIT licence or other open licences. A non-exhaustive list can be found in the [NOTICE](https://github.com/Eyra-is/Eyra/tree/master/NOTICE) document.
