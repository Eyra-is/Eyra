package is.eyra.eyra;

import android.media.MediaRecorder;
import android.util.Log;

import java.io.IOException;

/**
 * Created by matthiasp on 2/18/16.
 *
 * Code in part from http://developer.android.com/guide/topics/media/audio-capture.html
 * License: http://creativecommons.org/licenses/by/2.5/
 */
public class Recorder {

    private MediaRecorder mRecorder = null;

    private static final String LOG_TAG = "AudioRecord";
    private static String mFileName = null;


    public void startRecording() {
        mRecorder = new MediaRecorder();
        mRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
        mRecorder.setOutputFile(mFileName);
        mRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);

        try {
            mRecorder.prepare();
        } catch (IOException e) {
            Log.e(LOG_TAG, "prepare() failed");
        }

        mRecorder.start();
    }

    public void stopRecording() {
        mRecorder.stop();
        mRecorder.release();
        mRecorder = null;
    }

}
