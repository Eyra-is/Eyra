package is.eyra.eyra;

import android.content.Context;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;

import java.io.DataOutput;
import java.io.DataOutputStream;
import java.util.ArrayList;

/**
 * Created by matthiasp on 2/18/16.
 *
 * Simple class designed for multiple short recordings using android.media.AudioRecord.
 */
public class Recorder {

    private AudioRecord mAudioRecord = null;

    private static final int AUDIOSOURCE = MediaRecorder.AudioSource.VOICE_RECOGNITION;
    private static final int SAMPLERATE = 44100;
    private static final int CHANNELCONFIG = AudioFormat.CHANNEL_IN_MONO;
    private static final int AUDIOFORMAT = AudioFormat.ENCODING_PCM_16BIT;
    // might have to increase this buffer size if we get problems recording
    private static final int BUFFERSIZE = AudioRecord.getMinBufferSize(SAMPLERATE, CHANNELCONFIG, AUDIOFORMAT);

    private static final String LOG_TAG = "RecorderLog";

    private short[] audioBuffer = new short[BUFFERSIZE];
    private int streamPosition = 0;
    private ArrayList audioData = new ArrayList();

    public Recorder() {
        mAudioRecord = new AudioRecord(AUDIOSOURCE, SAMPLERATE, CHANNELCONFIG, AUDIOFORMAT, BUFFERSIZE);
    }

    public void startRecording() {
        mAudioRecord.startRecording();
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (mAudioRecord.getRecordingState() ==
                        AudioRecord.RECORDSTATE_RECORDING) {
                    int result = mAudioRecord.read(audioBuffer, 0, BUFFERSIZE);
                    streamPosition += BUFFERSIZE;

                    for (int i = 0; i < audioBuffer.length; i++) {
                        audioData.add(audioBuffer[i]);
                    }

                    try{
                        // sleep amount between AudioRecord.read() calls
                        Thread.sleep(50);
                    } catch(InterruptedException e){
                        e.printStackTrace();
                    }
                }
            }
        }, "AudioRecorder Thread").start();
    }

    public void stopRecording() {
        mAudioRecord.stop();
        Log.v(LOG_TAG, audioData.toString());

        int numChannels = CHANNELCONFIG == AudioFormat.CHANNEL_IN_MONO ? 1 : 2;
        RawToWav rtw = new RawToWav(SAMPLERATE, numChannels);
        Short[] tempData = new Short[audioData.size()];
        tempData = (Short[]) audioData.toArray(tempData);
        short[] data = new short[tempData.length];
        for (int i = 0; i < data.length; i++) {
            data[i] = tempData[i].shortValue();
        }
        DataOutputStream dos = rtw.convert(data);
        Log.v(LOG_TAG, dos.toString());
    }
}
