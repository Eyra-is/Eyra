/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

package is.eyra.eyra;

import android.net.http.SslError;
import android.util.Log;
import android.webkit.SslErrorHandler;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Created by matthiasp on 2/16/16.
 */
public class EyraWebViewClient extends WebViewClient {
    @Override
    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
        Log.v("DEBUG", view.toString());
        Log.v("DEBUG", handler.toString());
        Log.v("DEBUG", error.toString());

        // need to fix the certificate thing, this is only for development now
        handler.proceed(); // Ignore SSL certificate errors
    }
}
