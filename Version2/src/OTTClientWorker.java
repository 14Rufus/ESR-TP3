import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class OTTClientWorker implements Runnable{

    private final Socket clientSocket;
    private final PrintWriter out;
    private final BufferedReader in;

    public OTTClientWorker(Socket cS) throws IOException {
        this.clientSocket = cS;
        this.out = new PrintWriter(clientSocket.getOutputStream(),true);
        this.in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
    }

    public String sendMessage(String msg) throws IOException {
        out.println(msg);
        return in.readLine();
    }

    public void run() {
        String resp = null;
        try {
            while (true) {
                resp = sendMessage("hello server");
                if (resp.equals("hello client")) {
                    System.out.println("True");
                } else {
                    System.out.println("Error");
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
