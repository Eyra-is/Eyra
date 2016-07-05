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

import android.app.Activity;
import android.provider.Settings;
import android.util.Log;
import android.webkit.JavascriptInterface;

/**
 * Created by matthias on 4/28/16.
 *
 * Allows javascript code to get some constants from our app. E.g. device IMEI (which we actually use ANDROID_ID instead)
 */
public class ConstantsJSInterface {
    Activity mActivity;

    ConstantsJSInterface(Activity activity) {
        mActivity = activity;
    }

    @JavascriptInterface
    public String getImei() {
        String android_id = android.provider.Settings.System.getString(mActivity.getContentResolver(), Settings.Secure.ANDROID_ID);
        Log.v("DEBUG", "Android id returned: " + android_id);
        return android_id;
    }
}
