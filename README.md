# Eyra

Eyra provides tools for data gathering designed to be used to make speech corpora for under-resourced languages.  

Check out our site, [eyra.is](http://eyra.is/).

## Installation

Currently, the Eyra backend has to be run on Linux. Systems we've used are mainly **Debian 8** and **Ubuntu 14.04** to a lesser degree.

The recording devices themselves (phones, laptops, anything with a compatible browser) can use Chrome or Firefox. However, when using phones, we recommend using our Android app (located in `AndroidApp`). It bypasses a nasty bug we discovered where audio recorded through a phone's browser is 48kHz, but the data in it appears to be limited to 16kHz.
    
If you want Quality Control (QC) to work, you need to install Kaldi and more, look at how to set it up in DEVELOPER.md. 

### Laptop installation (local wifi)

Setup a laptop which the phones (recording devices) can connect to in an offline setting.

* **Backend (on the laptop)**  
    You have to initially have an internet connection and run  
    `./Setup/setup.sh --all`
    
* **Client-side (on the devices)**
    * Android app  
        1. Install `AndroidApp/versions/v1.4/app-debug-v1.4.apk` (or whatever is the latest version) on your phone.  
        2. Install the self-signed certificate on your phone (`Setup/src/apache/tmpl/etc_ssl_certs_rootCA.pem`)
        3. Connect to FeedMeData Wifi and start the Eyra Android app.
    * Straight outta browser  
        1. Connect to FeedMeData Wifi.
        2. Navigate to https://local.eyra.is
        3. Go to `Settings->Register device` (optional)
    
    Optionally, you can go to `Settings->Set instructor` if you want to link this device to a certain field worker/instructor.

### Internet installation (e.g. for crowdsourcing)

Setup a server (we use apache).

* **Backend**  
    Run `./Setup/setup.sh --all --no-ap`.

    You might want to look at `Setup/src/apache/tmpl/etc_apache2_sites-available_datatool.conf` (src) or `/etc/apache2/sites-enabled/datool.conf` (generated) and e.g. adjust the parameters for the `mpm_worker_module`.  

    The laptop setup uses a self-signed certificate (which needs to be manually put on and installed on the phones), but the internet one should use a real certificate (this depends on which certificate used). We used [letsencrypt](https://letsencrypt.org/) for a free certificate. This has to be done manually.
    
    This should work on both **Debian 8 Jessie** and **Ubuntu Server 14.04**.  
    
    
* **Client-side**  
    Same as the laptop installation, except, no need to manually install the certificates and of course the link to your server depends on where you host it (you might need to change this in the Android app code (see DEVELOPER.md for details)).
    

## Usage

### Basic usage:

In the GUI
1. Hit begin  
2. Type your username (anything)  
3. Enter your info (gender, etc.)
4. Hit Rec to start recording and display a prompt
5. Hit Stop when you have read the prompt


TODO: Write more detailed usage / provide link to it.


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature` (try to follow [this](https://gist.github.com/dmglab/8402579#allowed-prefixes) convention)
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

See a list of our todos in TODOS.md and TODOS_QC.md.  
Look at DEVELOPER.md for much more detailed info on how the software operates.


## Credits

This project wouldn't have been possible without the cooperation of 

* Google

along with constant vigilance as project head by

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


## License

This software is licenced under the Apache Version 2.0 licence as stated in the LICENCE document. Some parts of the software are licenced under the MIT licence or other open licences. These differences are noted in NOTICE document. 


