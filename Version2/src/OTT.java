import java.io.IOException;
import java.net.*;

public class OTT {


    public static void main(String[] args) throws IOException, InterruptedException {

        ServerSocket serverSocket = new ServerSocket(9999);
        Socket clientSocket = new Socket("127.0.0.1",9999);

        Thread s = new Thread(new Node(serverSocket,clientSocket));
        Thread c = new Thread(new OTTClientWorker(clientSocket));


        s.start();
        c.start();

        s.join();
        c.join();
    }
}
