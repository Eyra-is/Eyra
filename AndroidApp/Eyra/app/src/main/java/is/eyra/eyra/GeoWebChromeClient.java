package is.eyra.eyra;

import android.webkit.GeolocationPermissions;
import android.webkit.WebChromeClient;

/**
 * Created by matthiasp on 2/18/16.
 *
 * Thanks David Chandler, https://turbomanage.wordpress.com/2012/04/23/how-to-enable-geolocation-in-a-webview-android/
 */
public class GeoWebChromeClient extends WebChromeClient {
    @Override
    public void onGeolocationPermissionsShowPrompt(String origin,
                                                   GeolocationPermissions.Callback callback) {
        // Always grant permission since the app itself requires location
        // permission and the user has therefore already granted it
        callback.invoke(origin, true, false);
    }
}
