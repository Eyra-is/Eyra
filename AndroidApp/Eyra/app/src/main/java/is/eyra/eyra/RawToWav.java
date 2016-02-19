package is.eyra.eyra;

import android.os.Environment;
import android.util.Log;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * Created by matthiasp on 2/18/16.
 *
 * Class designed to convert audio data from AudioRecord to .wav files.
 */
public class RawToWav {

    private int mSampleRate;
    private int mNumChannels;

    RawToWav(int sampleRate, int numChannels) {
        mSampleRate = sampleRate;
        mNumChannels = numChannels;
    }

    public DataOutputStream convert(short[] raw) {
        DataOutputStream outFile = null;
        try {
            outFile = new DataOutputStream(
                new FileOutputStream (
                    new File(
                        Environment.getExternalStorageDirectory().getAbsolutePath() + "/testBlob.wav"
                    ), true
                )
            );
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            // write WAV header
            outFile.writeBytes("RIFF");
            //Log.v("RawToWav", String.valueOf(36 + raw.length * 2));
            outFile.write(intToBytes(36 + raw.length * 2, "LITTLE_ENDIAN"), 0, 4);
            outFile.writeBytes("WAVE");
            outFile.writeBytes("fmt ");
            outFile.write(intToBytes(16, "LITTLE_ENDIAN"), 0, 4);
            outFile.write(shortToBytes((short) 1, "LITTLE_ENDIAN"), 0, 2);
            outFile.write(shortToBytes((short) mNumChannels, "LITTLE_ENDIAN"), 0, 2);
            outFile.write(intToBytes(mSampleRate, "LITTLE_ENDIAN"), 0, 4);
            outFile.write(intToBytes(mSampleRate * mNumChannels * 2, "LITTLE_ENDIAN"), 0, 4);
            outFile.write(shortToBytes((short) (mNumChannels * 2), "LITTLE_ENDIAN"), 0, 2);
            outFile.write(shortToBytes((short) 16, "LITTLE_ENDIAN"), 0, 2);
            outFile.writeBytes("data");
            outFile.write(intToBytes(raw.length * 2, "LITTLE_ENDIAN"), 0, 4);
            // write WAV data
            for (int i = 0; i < raw.length; i++) {
                outFile.write(shortToBytes(raw[i], "LITTLE_ENDIAN"), 0, 2);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return outFile;
    }

    private byte[] intToBytes(int a, String endian) {
        ByteBuffer b = ByteBuffer.allocate(4);
        if (endian.equals("LITTLE_ENDIAN")) {
            b.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            b.order(ByteOrder.BIG_ENDIAN);
        }
        b.putInt(a);
        return b.array();
    }
    private byte[] shortToBytes(short a, String endian) {
        ByteBuffer b = ByteBuffer.allocate(4);
        if (endian.equals("LITTLE_ENDIAN")) {
            b.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            b.order(ByteOrder.BIG_ENDIAN);
        }
        b.putShort(a);
        return b.array();
    }
}
