package is.eyra.eyra;

import android.content.Context;
import android.webkit.JavascriptInterface;

/**
 * Created by matthiasp on 2/18/16.
 *
 * The JS object
 */
public class RecorderJSInterface {

    private Recorder recorder = null;

    public RecorderJSInterface() {
        recorder = new Recorder();
    }

    @JavascriptInterface
    public void startRecording() {
        recorder.startRecording();
    }

    @JavascriptInterface
    public void stopRecording() {
        recorder.stopRecording();
    }

    @JavascriptInterface
    public String toString() { return "Hello android/js world!"; }
}
