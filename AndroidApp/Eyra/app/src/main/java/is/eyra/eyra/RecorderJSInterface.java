/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/*
File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

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

    // returns a wav file of the recording as a byte array on json format (Arrays.toString should be valid json).
    // for example: returns "[82,73,70,70,36,16,3,0,87,65,86,69, ...]"
    @JavascriptInterface
    public String stopRecording() {
        Log.v("DEBUG", "STOPPED REC");
        byte[] wav = recorder.stopRecording();
        return Arrays.toString(wav);
    }

    @JavascriptInterface
    public String toString() { return "Hello android/js world!"; }
}
