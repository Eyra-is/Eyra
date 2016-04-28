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

    // returns a wav file of the recording as a byte array serialized as json.
    // for example: returns "[82,73,70,70,36,16,3,0,87,65,86,69, ...]"
    @JavascriptInterface
    public String stopRecording() {
        Log.v("DEBUG", "STOPPED REC");
        byte[] wav = recorder.stopRecording();
        // for some reason, for this JSONArray thing, it needs Byte[] not byte[]
        Byte[] objWav = new Byte[wav.length];
        for (int i = 0; i < objWav.length; i++) {
            objWav[i] = wav[i];
        }
        return new JSONArray(Arrays.asList(objWav)).toString();
    }

    @JavascriptInterface
    public String toString() { return "Hello android/js world!"; }
}
