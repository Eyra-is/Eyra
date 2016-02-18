package is.eyra.eyra;

import android.media.MediaRecorder;
import android.os.Environment;
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
    private static String mFileName = null;

    private static final String LOG_TAG = "RecorderLog";

    public Recorder() {
        mFileName = Environment.getExternalStorageDirectory().getAbsolutePath();
        mFileName += "/audiorecordtest.3gp";
    }

    public void startRecording() {
        mRecorder = new MediaRecorder();
        mRecorder.setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION);
        mRecorder.setOutputFormat(MediaRecorder.OutputFormat.ENCODING_PCM_16BIT);
        mRecorder.setOutputFile(mFileName);
        mRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);
        //mRecorder.setAudioChannels(1);
        //mRecorder.setAudioEncodingBitRate(128000);
        //mRecorder.setAudioSamplingRate(44100);

        try {
            mRecorder.prepare();
        } catch (IOException e) {
            Log.e(LOG_TAG, "prepare() failed");
        }

        mRecorder.start();
    }

    public void stopRecording() {
        mRecorder.stop();
        //mRecorder.reset();    // http://stackoverflow.com/a/11984387/5272567
        mRecorder.release();
        mRecorder = null;
    }
}
