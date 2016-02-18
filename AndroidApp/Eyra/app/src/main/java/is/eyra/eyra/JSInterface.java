package is.eyra.eyra;

import android.webkit.JavascriptInterface;

/**
 * Created by matthiasp on 2/18/16.
 */
public class JSInterface {
    @JavascriptInterface
    public String toString() { return "Hello android/js world!"; }
}
