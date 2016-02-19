package is.eyra.eyra;

import android.util.Log;
import android.webkit.JavascriptInterface;
import org.json.JSONArray;

import java.util.Arrays;

/**
 * Created by matthiasp on 2/18/16.
 *
 * The JS recorder object passed to our web app.
 */
public class RecorderJSInterface {

    private Recorder recorder = null;

    public RecorderJSInterface() {
        recorder = new Recorder();
    }

    @JavascriptInterface
    public void startRecording() {
        Log.v("DEBUG", "START REC");
        recorder.startRecording();
    }

    @JavascriptInterface
    public String stopRecording() {
        Log.v("DEBUG", "STOPPED REC");
        byte[] wav = recorder.stopRecording();
        return new JSONArray(Arrays.asList(wav)).toString();
    }

    @JavascriptInterface
    public String toString() { return "Hello android/js world!"; }
}
