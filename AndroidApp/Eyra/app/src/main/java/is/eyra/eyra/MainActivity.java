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

import io.fabric.sdk.android.Fabric;

public class MainActivity extends AppCompatActivity {

    private WebView mWebView;
    // permission request codes for requestPermissions()
    private static final int LOCATION_REQUESTCODE = 100;
    private static final int RECORDING_REQUESTCODE = 101;

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

        // so long as we are in Android Marshmallow, we need to do this at runtime.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            requestOurPermissions();
        }

        mWebView.addJavascriptInterface(new RecorderJSInterface(), "AndroidRecorder");

        // Enable Javascript
        WebSettings webSettings = mWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        // Enable DOM storage, thanks Lewis, http://stackoverflow.com/a/29978620/5272567
        webSettings.setDomStorageEnabled(true);
        // Force links and redirects to open in the WebView instead of in a browser
        mWebView.setWebViewClient(new EyraWebViewClient());
        // Allow location
        mWebView.setWebChromeClient(new GeoWebChromeClient());

        // enable appcache
        webSettings.setDomStorageEnabled(true);
        webSettings.setAppCachePath("/data/data/" + getPackageName() + "/cache");
        webSettings.setAllowFileAccess(true);
        webSettings.setAppCacheEnabled(true);
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);

        mWebView.loadUrl("https://jv.eyra.is/"); //(getString(R.string.website_url));
        //mWebView.loadUrl("http://beta.html5test.com/");
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

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @TargetApi(android.os.Build.VERSION_CODES.M) // marhsmallow
    private void requestOurPermissions() {
        /*
            !!! This function should only be called if we are in Android M or higher. !!!
            make sure we have location (optional) and recording (mandatory) permissions.
         */
        String locPermission = Manifest.permission.ACCESS_FINE_LOCATION;
        String recPermission = Manifest.permission.RECORD_AUDIO;
        if (checkSelfPermission(locPermission) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{locPermission}, LOCATION_REQUESTCODE);
        }

        if (checkSelfPermission(recPermission) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{recPermission}, RECORDING_REQUESTCODE);
        }
    }

    @Override
    public void onRequestPermissionsResult (int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == LOCATION_REQUESTCODE) {
            // do nothing. Location permission is not mandatory.
            Log.v("DEBUG", "Location granted? " + (grantResults[0] == PackageManager.PERMISSION_GRANTED));
        }

        if (requestCode == RECORDING_REQUESTCODE) {
            // make sure we have recording permissions, otherwise app is unusable.
            Log.v("DEBUG", "Recording granted? " + (grantResults[0] == PackageManager.PERMISSION_GRANTED));

            boolean granted = grantResults[0] == PackageManager.PERMISSION_GRANTED;
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

    public void forceCrash(View view) {
        throw new RuntimeException("This is a crash");
    }
}
