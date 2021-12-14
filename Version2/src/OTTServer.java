import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class OTTServer {

    public static void main(String[] args) throws IOException {

        BufferedReader in;
        PrintWriter out;
        ServerSocket serverSocket = new ServerSocket(8080);

        while (true){
            Socket clientSocket = serverSocket.accept();
            in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            out = new PrintWriter(clientSocket.getOutputStream(), true);

            while(true) {
                String msg = in.readLine();
                System.out.println(msg);
            }
        }

    }

}
