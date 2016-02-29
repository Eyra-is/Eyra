package is.eyra.eyra;

import android.os.Environment;
import android.util.Log;

import java.io.ByteArrayOutputStream;
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

    public byte[] convert(short[] raw) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        try {
            // write WAV header
            // reference for wav header: recorder.js by matt diamond, https://github.com/mattdiamond/Recorderjs
            // and http://stackoverflow.com/a/5810662/5272567 by
            //   user663321, Evan Merz and Dan Vargo
            baos.write(new byte[]{'R', 'I', 'F', 'F'}, 0, 4);
            baos.write(intToBytes(36 + raw.length * 2, "LITTLE_ENDIAN"), 0, 4);
            baos.write(new byte[]{'W', 'A', 'V', 'E'}, 0, 4);
            baos.write(new byte[]{'f', 'm', 't', ' '}, 0, 4);
            baos.write(intToBytes(16, "LITTLE_ENDIAN"), 0, 4);
            baos.write(shortToBytes((short) 1, "LITTLE_ENDIAN"), 0, 2);
            baos.write(shortToBytes((short) mNumChannels, "LITTLE_ENDIAN"), 0, 2);
            baos.write(intToBytes(mSampleRate, "LITTLE_ENDIAN"), 0, 4);
            baos.write(intToBytes(mSampleRate * mNumChannels * 2, "LITTLE_ENDIAN"), 0, 4);
            baos.write(shortToBytes((short) (mNumChannels * 2), "LITTLE_ENDIAN"), 0, 2);
            baos.write(shortToBytes((short) 16, "LITTLE_ENDIAN"), 0, 2);
            baos.write(new byte[]{'d', 'a', 't', 'a'}, 0, 4);
            baos.write(intToBytes(raw.length * 2, "LITTLE_ENDIAN"), 0, 4);
            // write WAV data
            // turn short array to byte array, compliments of Peter Lawrey, http://stackoverflow.com/a/5626003/5272567
            byte[] byteData = new byte[raw.length * 2];
            ByteBuffer.wrap(byteData).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().put(raw);
            baos.write(byteData, 0, byteData.length);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return baos.toByteArray();
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
