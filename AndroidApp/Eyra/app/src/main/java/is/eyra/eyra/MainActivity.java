/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

package is.eyra.eyra;

import android.Manifest;
import android.annotation.TargetApi;
import android.app.Activity;
import android.content.DialogInterface;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.provider.Settings;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import com.crashlytics.android.Crashlytics;

import java.util.ArrayList;
import java.util.List;

import io.fabric.sdk.android.Fabric;

public class MainActivity extends AppCompatActivity {

    private WebView mWebView;
    private WebSettings mWebSettings;
    // permission request codes for requestPermissions()
    private static final int APPSTART_REQUESTCODE = 101;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Fabric.with(this, new Crashlytics());
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // only for development, or not
        /*FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mWebView.reload();
            }
        });*/

        mWebView = (WebView) findViewById(R.id.activity_main_webview);
        mWebSettings = mWebView.getSettings();

        // so long as we are in Android Marshmallow, we need to do this at runtime.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            requestOurPermissions();
        }

        addAppVersionToUserAgent();

        mWebView.addJavascriptInterface(new RecorderJSInterface(), "AndroidRecorder");
        mWebView.addJavascriptInterface(new ConstantsJSInterface(this), "AndroidConstants");

        // Enable Javascript
        mWebSettings.setJavaScriptEnabled(true);
        // Enable DOM storage, thanks Lewis, http://stackoverflow.com/a/29978620/5272567
        mWebSettings.setDomStorageEnabled(true);
        // Force links and redirects to open in the WebView instead of in a browser
        mWebView.setWebViewClient(new EyraWebViewClient());
        // Allow location
        mWebView.setWebChromeClient(new GeoWebChromeClient());

        // enable appcache
        mWebSettings.setDomStorageEnabled(true);
        mWebSettings.setAppCachePath("/data/data/" + getPackageName() + "/cache");
        mWebSettings.setAllowFileAccess(true);
        mWebSettings.setAppCacheEnabled(true);
        mWebSettings.setCacheMode(WebSettings.LOAD_DEFAULT);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            mWebView.setWebContentsDebuggingEnabled(true);
        }

        mWebView.loadUrl(getString(R.string.website_url));
    }

    private void addAppVersionToUserAgent() {
        /* appends "App version: x.x " to the user agent string webview normally generates. */
        String versionName = BuildConfig.VERSION_NAME;
        if (versionName == null || versionName.equals("")) {
            versionName = "0.0";
        }
        mWebSettings.setUserAgentString(
                "App version: "+versionName+
                " "+
                mWebSettings.getUserAgentString());

        Log.v("DEBUG", "User agent string changed to: " + mWebSettings.getUserAgentString());
    }

    // code from here: https://developer.chrome.com/multidevice/webview/gettingstarted
    // license: http://creativecommons.org/licenses/by/3.0/
    @Override
    public void onBackPressed() {
        if(mWebView.canGoBack()) {
            mWebView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @TargetApi(android.os.Build.VERSION_CODES.M) // marhsmallow
    private void requestOurPermissions() {
        /*
            !!! This function should only be called if we are in Android M or higher. !!!
            make sure we have location (optional) and recording (mandatory) permissions.
         */
        String locPermission = Manifest.permission.ACCESS_FINE_LOCATION;
        String recPermission = Manifest.permission.RECORD_AUDIO;
        List<String> permissions = new ArrayList<String>();
        if (checkSelfPermission(locPermission) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(locPermission);
        }
        if (checkSelfPermission(recPermission) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(recPermission);
        }
        if (permissions.size() > 0) {
            requestPermissions(permissions.toArray(new String[permissions.size()]), APPSTART_REQUESTCODE);
        }
    }

    @Override
    public void onRequestPermissionsResult (int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == APPSTART_REQUESTCODE) {
            if (permissions.length < 1 || permissions.length > 2) {
                throw new IllegalArgumentException("Somethings is wrong, permissions asked should have 1 or 2 elements, has: " + permissions.length + " elements.");
            }

            int locIndex = -1;
            int recIndex = -1;
            // find which index in grantResults belongs to location and or recordings
            for (int i = 0; i < permissions.length; i++) {
                if (permissions[i].equals(Manifest.permission.ACCESS_FINE_LOCATION)) {
                    locIndex = i;
                }
                if (permissions[i].equals(Manifest.permission.RECORD_AUDIO)) {
                    recIndex = i;
                }
            }

            // handle location
            if (locIndex != -1) {
                // do nothing special with location. Location permission is not mandatory.
                Log.v("DEBUG", "Location granted? " + (grantResults[locIndex] == PackageManager.PERMISSION_GRANTED));
            }

            // handle recording
            if (recIndex != -1) {
                // make sure we have recording permissions, otherwise app is unusable.
                boolean granted = grantResults[recIndex] == PackageManager.PERMISSION_GRANTED;
                Log.v("DEBUG", "Recording granted? " + granted);
                if (!granted) {
                    final Activity main = this;

                    // thanks Ye Lin Aung @
                    // http://stackoverflow.com/questions/18371883/how-to-create-modal-dialog-box-in-android
                    AlertDialog.Builder alert = new AlertDialog.Builder(this);
                    alert.setTitle("Recording permission needed!");
                    alert.setMessage("You have to allow recording for this app to work. App will exit.");
                    alert.setCancelable(false);
                    alert.setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                            main.finish(); // "exit" application. Minimizes it, but it should request permissions on start again.
                        }
                    });
                    alert.show();
                }
            }

        }
    }

    public void forceCrash(View view) {
        throw new RuntimeException("This is a crash");
    }
}
