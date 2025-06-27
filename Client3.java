// import java.io.*;
// import java.net.*;

// public class Client3 {
//     private static final String SERVER_IP = "127.0.0.1";
//     private static final int SERVER_PORT = 8000;
//     private static final String OUTPUT_FILE = "live_stream_received.bin";  // 실제 mp4가 아님!

//     public static void main(String[] args) {
//         try (
//             Socket socket = new Socket(SERVER_IP, SERVER_PORT);
//             OutputStream out = socket.getOutputStream();
//             InputStream in = socket.getInputStream();
//             FileOutputStream fileOut = new FileOutputStream(OUTPUT_FILE)
//         ) {
//             System.out.println("[Client 3] Connected to local server");

//             // 1. 요청 전송
//             out.write("live".getBytes());
//             out.flush();
//             socket.shutdownOutput();  // 요청 종료

//             // 2. JPEG 프레임 저장
//             while (true) {
//                 // 2-1. 4바이트 헤더 수신
//                 byte[] header = new byte[4];
//                 if (!recvExact(in, header, 4)) break;

//                 int size = byteArrayToInt(header);
//                 if (size <= 0) break;

//                 // 2-2. 프레임 수신
//                 byte[] frameData = new byte[size];
//                 if (!recvExact(in, frameData, size)) break;

//                 // 2-3. 파일에 원시 저장 (향후 viewer.py가 처리 가능하게)
//                 fileOut.write(header);
//                 fileOut.write(frameData);
//             }

//             System.out.println("[Client 3] Live stream saved to '" + OUTPUT_FILE + "'");

//         } catch (IOException e) {
//             System.err.println("[Client 3 Error] " + e.getMessage());
//         }

//         // 3. viewer 실행 (viewer는 프레임 구조 해석해서 영상화해야 함)
//         try {
//             String[] fullCmd = {
//                 "cmd", "/c", "start", "\"Viewer\"", "python", "viewer_stream.py", "live_stream_received.bin", "LIVE"
//             };

//             System.out.println("[Client 3] Launching viewer...");
//             new ProcessBuilder(fullCmd).inheritIO().start();

//         } catch (IOException e) {
//             System.err.println("[Viewer Launch Error] " + e.getMessage());
//         }
//     }

//     // 정확히 N바이트 수신
//     private static boolean recvExact(InputStream in, byte[] buffer, int size) throws IOException {
//         int total = 0;
//         while (total < size) {
//             int bytes = in.read(buffer, total, size - total);
//             if (bytes == -1) return false;
//             total += bytes;
//         }
//         return true;
//     }

//     // 4바이트 big-endian → int 변환
//     private static int byteArrayToInt(byte[] b) {
//         return ((b[0] & 0xFF) << 24) |
//                ((b[1] & 0xFF) << 16) |
//                ((b[2] & 0xFF) << 8) |
//                (b[3] & 0xFF);
//     }
// }


import java.io.*;
import java.net.*;
import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

public class Client3 {
    private static final String SERVER_IP = "127.0.0.1";
    private static final int SERVER_PORT = 8000;

    public static void main(String[] args) {
        try (
            Socket socket = new Socket(SERVER_IP, SERVER_PORT);
            OutputStream out = socket.getOutputStream();
            InputStream in = socket.getInputStream()
        ) {
            System.out.println("[Client 3] Connected to local server");

            // 1. 요청 전송
            out.write("live".getBytes());
            out.flush();
            socket.shutdownOutput();

            // 2. GUI 준비
            JFrame frame = new JFrame("Client3 - LIVE Stream");
            JLabel label = new JLabel();
            frame.getContentPane().add(label, BorderLayout.CENTER);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(500, 400);
            frame.setVisible(true);

            // 3. 수신 및 표시
            while (true) {
                byte[] header = new byte[4];
                if (!recvExact(in, header, 4)) break;
                int size = byteArrayToInt(header);
                if (size <= 0) break;

                byte[] frameData = new byte[size];
                if (!recvExact(in, frameData, size)) break;

                ByteArrayInputStream bais = new ByteArrayInputStream(frameData);
                BufferedImage img = ImageIO.read(bais);
                if (img != null) {
                    ImageIcon icon = new ImageIcon(img.getScaledInstance(480, 360, Image.SCALE_SMOOTH));
                    label.setIcon(icon);
                    frame.repaint();
                }
            }

            System.out.println("[Client 3] Stream ended.");

        } catch (IOException e) {
            System.err.println("[Client 3 Error] " + e.getMessage());
        }
    }

    private static boolean recvExact(InputStream in, byte[] buffer, int size) throws IOException {
        int total = 0;
        while (total < size) {
            int bytes = in.read(buffer, total, size - total);
            if (bytes == -1) return false;
            total += bytes;
        }
        return true;
    }

    private static int byteArrayToInt(byte[] b) {
        return ((b[0] & 0xFF) << 24) |
               ((b[1] & 0xFF) << 16) |
               ((b[2] & 0xFF) << 8) |
               (b[3] & 0xFF);
    }
}
