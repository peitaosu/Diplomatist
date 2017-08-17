/* Some Code Fragments from:
   1. https://stackoverflow.com/questions/18812224/c-sharp-recording-audio-from-soundcard - Florian R.
 */

using System;
using CSCore.SoundIn;
using CSCore.Codecs.WAV;

namespace SoundsRecord
{
    class Program
    {
        static void Main(string[] args)
        {
            using (WasapiCapture capture = new WasapiLoopbackCapture())
            {

                //initialize the selected device for recording
                capture.Initialize();

                //create a wavewriter to write the data to
                using (WaveWriter w = new WaveWriter("dump.wav", capture.WaveFormat))
                {
                    //setup an eventhandler to receive the recorded data
                    capture.DataAvailable += (s, e) =>
                    {
                        //save the recorded audio
                        w.Write(e.Data, e.Offset, e.ByteCount);
                    };

                    //start recording
                    capture.Start();

                    Console.ReadKey();

                    //stop recording
                    capture.Stop();
                }
            }
        }
    }
}
