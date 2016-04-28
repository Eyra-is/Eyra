package is.eyra.eyra;

import android.app.Activity;
import android.provider.Settings;
import android.util.Log;
import android.webkit.JavascriptInterface;

/**
 * Created by matthias on 4/28/16.
 *
 * Allows javascript code to get some constants from our app. E.g. device IMEI (which we actually use ANDROID_ID instead)
 */
public class ConstantsJSInterface {
    Activity mActivity;

    ConstantsJSInterface(Activity activity) {
        mActivity = activity;
    }

    @JavascriptInterface
    public String getImei() {
        String android_id = android.provider.Settings.System.getString(mActivity.getContentResolver(), Settings.Secure.ANDROID_ID);
        Log.v("DEBUG", "Android id returned: " + android_id);
        return android_id;
    }
}
