/* Some Code Fragments from:
   1. https://stackoverflow.com/questions/18812224/c-sharp-recording-audio-from-soundcard - Florian R.
 */

using System;
using CSCore.SoundIn;
using CSCore.Codecs.WAV;
using System.Threading;

namespace SoundsRecord
{
    class Program
    {
        static int Main(string[] args)
        {
            if (args.Length == 0 || args[0] == "-h" || args[0] == "--help")
            {
                System.Console.WriteLine("Usage:");
                System.Console.WriteLine("    SoundsRecord.exe <time/seconds> <output/wav>");
                return 1;
            }

            using (WasapiCapture capture = new WasapiLoopbackCapture())
            {

                //initialize the selected device for recording
                capture.Initialize();

                //create a wavewriter to write the data to
                using (WaveWriter w = new WaveWriter(args[1], capture.WaveFormat))
                {
                    //setup an eventhandler to receive the recorded data
                    capture.DataAvailable += (s, e) =>
                    {
                        //save the recorded audio
                        w.Write(e.Data, e.Offset, e.ByteCount);
                    };

                    //start recording
                    capture.Start();

                    //delay and keep recording
                    Thread.Sleep(Int32.Parse(args[0]) * 1000);

                    //stop recording
                    capture.Stop();
                }
            }
            return 0;
        }
    }
}
