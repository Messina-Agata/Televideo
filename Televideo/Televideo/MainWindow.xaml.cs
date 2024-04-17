using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Net;
using System.IO;
using System.Text.RegularExpressions;

namespace Televideo
{
    /// <summary>
    /// Logica di interazione per MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        ScrollViewer viewer = new ScrollViewer();
        StackPanel container = new StackPanel();

        private string[] programs;

        private struct channel
        {
            public string name;
            public string url;
        };
        private channel[] channels;

        public MainWindow()
        {
            InitializeComponent();
            findChannels();
            viewer.VerticalScrollBarVisibility = ScrollBarVisibility.Visible;
            viewer.Content = container;
            window.Content = viewer;

            insertProgramsToSearch();
        }

        private void addTextBlock(string text, int tag)
        {
            TextBlock title = new TextBlock();
            title.Text = text;
            title.Height = 30;
            title.FontSize = 20;
            title.HorizontalAlignment = HorizontalAlignment.Center;
            title.VerticalAlignment = VerticalAlignment.Center;
            title.Tag = tag;
            container.Children.Add(title);
        }

        private void addStackPanelWithTextBoxAndButton(string line, int tag)
        {
            StackPanel st1 = new StackPanel();
            st1.HorizontalAlignment = HorizontalAlignment.Center;
            st1.VerticalAlignment = VerticalAlignment.Center;
            st1.Width = 400;
            st1.Orientation = Orientation.Horizontal;
            TextBox tb = new TextBox();
            tb.Text = line;
            tb.TextAlignment = TextAlignment.Center;
            tb.Height = 30;
            tb.Width = 300;
            tb.FontSize = 20;
            tb.HorizontalAlignment = HorizontalAlignment.Center;
            tb.VerticalAlignment = VerticalAlignment.Center;
            tb.LostFocus += new RoutedEventHandler(textBox_LostFocus);
            st1.Children.Add(tb);
            Button b = new Button();
            b.Content = "Rimuovi";
            b.Height = 30;
            b.Width = 100;
            b.Click += new RoutedEventHandler(removeButton_Click);
            st1.Tag = tag;
            st1.Children.Add(b);
            container.Children.Add(st1);
        }

        private void addStackPanelWithAddAndSearchButtons(int tag)
        {
            StackPanel st2 = new StackPanel();
            st2.HorizontalAlignment = HorizontalAlignment.Center;
            st2.VerticalAlignment = VerticalAlignment.Center;
            st2.Width = 400;
            st2.Orientation = Orientation.Horizontal;
            Button addButton = new Button();
            addButton.Content = "Aggiungi programma";
            addButton.Height = 30;
            addButton.Width = 200;
            addButton.Click += new RoutedEventHandler(addButton_Click);
            st2.Children.Add(addButton);
            Button searchButton = new Button();
            searchButton.Content = "Cerca programmi";
            searchButton.Height = 30;
            searchButton.Width = 200;
            searchButton.Click += new RoutedEventHandler(searchButton_Click);
            st2.Children.Add(searchButton);
            st2.Tag = tag;
            container.Children.Add(st2);
        }

        private void showErrorMessage(string text)
        {
            TextBlock warning = new TextBlock();
            warning.Text = text;
            warning.HorizontalAlignment = HorizontalAlignment.Center;
            Thickness margin = warning.Margin;
            margin.Top = 10;
            warning.Margin = margin;
            warning.Background = new SolidColorBrush(Colors.Red);
            container.Children.Add(warning);
        }

        private void insertProgramsToSearch()
        {
            int i = 0;
            addTextBlock("Programmi da cercare", i++);

            try
            {
                string[] lines = File.ReadAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"));
                foreach (string line in lines)
                {
                    addStackPanelWithTextBoxAndButton(line, i++);
                }
            }
            catch(FileNotFoundException)
            {
                
            }
            finally
            {
                addStackPanelWithAddAndSearchButtons(i++);
            }
            
        }

        private void searchButton_Click (object sender, RoutedEventArgs e)
        {
            loadProgramsToSearch();
            if (programs == null)
                return;
            int index = (int)((StackPanel)((Button)sender).Parent).Tag;
            if (container.Children.Count > index)
                container.Children.RemoveRange(++index, container.Children.Count);
            findPrograms(++index);
        }

        private void textBox_LostFocus(object sender, RoutedEventArgs e)
        {
            int index = (int)((StackPanel)((TextBox)sender).Parent).Tag;
            try
            {
                string[] lines = File.ReadAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"));
                if (index > lines.Length)
                {
                    string[] newLines = new string[lines.Length + 1];
                    for (int i = 0; i < lines.Length; i++)
                    {
                        newLines[i] = lines[i];
                    }
                    newLines[lines.Length] = ((TextBox)sender).Text;
                    File.WriteAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"), newLines);
                }
                else
                {
                    lines[index - 1] = ((TextBox)sender).Text;
                    File.WriteAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"), lines);
                }
            }
            catch (FileNotFoundException)
            {
                string[] newLine = new string[] { ((TextBox)sender).Text };
                File.WriteAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"), newLine);
            }
        }

        private void addButton_Click(object sender, RoutedEventArgs e)
        {
            int index = (int)((StackPanel)((Button)sender).Parent).Tag;
            container.Children.RemoveRange(index, container.Children.Count);

            addStackPanelWithTextBoxAndButton("", index++);
            addStackPanelWithAddAndSearchButtons(index++);
        }

        private void removeButton_Click(object sender, RoutedEventArgs e)
        {
            int index = (int)((StackPanel)((Button)sender).Parent).Tag;
            try
            {
                string[] lines = File.ReadAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"));
                if (index <= lines.Length)
                {
                    string[] newLines = new string[lines.Length - 1];
                    int j = 0;
                    for (int i = 0; i < lines.Length; i++)
                    {
                        if (i != index - 1)
                            newLines[j++] = lines[i];
                    }
                    File.WriteAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"), newLines);
                }
            }
            catch (FileNotFoundException)
            {
                
            }
            finally
            {
                container.Children.RemoveRange(0, container.Children.Count);
                insertProgramsToSearch();
            }
        }

        private void loadProgramsToSearch()
        {
            try
            {
                string[] lines = File.ReadAllLines(System.IO.Path.Combine(Environment.CurrentDirectory, "../../conf/programs.txt"));
                programs = new string[lines.Length];
                int i = 0;
                foreach (string line in lines)
                    programs[i++] = line;
            }
            catch (FileNotFoundException)
            {
                showErrorMessage("Nessun programma inserito");
            }
            
        }

        private void findChannels()
        {
            string sURL = "https://guidatv.quotidiano.net/";
            string siteContent = getWebPage(sURL);
            Regex rx = new Regex("(?<=channel channel-thumbnail)(.*?)(?=title)", RegexOptions.IgnoreCase);
            MatchCollection matches = rx.Matches(siteContent);
            Regex rx2 = new Regex("(?<=\"channel-name\">)(.*?)(?=</span>)", RegexOptions.IgnoreCase);
            MatchCollection matches2 = rx2.Matches(siteContent);
            channels = new channel[matches.Count];
            for (int ctr = 0; ctr < matches.Count; ctr++)
            {
                rx = new Regex("(?<=a href=\"/)(.*?)(?=\")", RegexOptions.IgnoreCase);
                MatchCollection match = rx.Matches(matches[ctr].Value);
                channels[ctr].url = sURL + match[0].Value;
                channels[ctr].name = matches2[ctr].Value;
            }
        }

        private string getWebPage(string url)
        {
            WebRequest wrGETURL = WebRequest.Create(url);
            Stream objStream;
            try
            {
                objStream = wrGETURL.GetResponse().GetResponseStream();
                StreamReader objReader = new StreamReader(objStream);
                if (objReader == null)
                {
                    showErrorMessage("Impossibile connettersi a " + url);
                    return "";
                }
                string sLine = "";
                string siteContent = "";
                int i = 0;
                while (sLine != null)
                {
                    i++;
                    try
                    {
                        sLine = objReader.ReadLine();
                    }
                    catch (IOException)
                    {
                        showErrorMessage("Errore di connessione");
                        return "";
                    }

                    if (sLine != null)
                        siteContent += sLine;
                }
                return siteContent;
            }
            catch (WebException)
            {
                showErrorMessage("Errore di connessione");
                return "";
            }
            
        }

        private void findPrograms(int count)
        {
            DateTime today = DateTime.Today;
            for (int j = 0; j < channels.Length; j++) {
                for (int d = 0; d < 7; d++)
                {
                    DateTime day = today.AddDays(d);
                    string dayString = day.ToString("dd-MM-yyyy");
                    string siteContent = getWebPage(channels[j].url + dayString);
                    if (siteContent.Equals(""))
                        return;
                    int startIndex = siteContent.IndexOf("<section id=\"faqs\">");
                    if (startIndex < 0)
                        continue;
                    siteContent = siteContent.Substring(startIndex);
                    int endIndex = siteContent.IndexOf("</li></ul>");
                    siteContent = siteContent.Substring(0, endIndex);
                    Regex rx = new Regex("(?<=<li>)(.*?)(?=</li>)", RegexOptions.IgnoreCase);
                    MatchCollection matches = rx.Matches(siteContent);

                    for (int ctr = 0; ctr < matches.Count; ctr++)
                    {
                        for (int k = 0; k < programs.Length; k++)
                        {
                            if (matches[ctr].Value.IndexOf(programs[k], StringComparison.OrdinalIgnoreCase) >= 0)
                            {
                                TextBlock found = new TextBlock();
                                found.Text = programs[k];
                                found.Height = 30;
                                found.FontSize = 20;
                                found.HorizontalAlignment = HorizontalAlignment.Center;
                                found.VerticalAlignment = VerticalAlignment.Center;
                                found.Background = new SolidColorBrush(Colors.LightSkyBlue);
                                Thickness margin = found.Margin;
                                margin.Top = 10;
                                found.Margin = margin;
                                container.Children.Add(found);
                                TextBlock found2 = new TextBlock();
                                found2.Text = dayString + " " + channels[j].name + " " + matches[ctr].Value;
                                found2.Height = 30;
                                found2.FontSize = 20;
                                found2.HorizontalAlignment = HorizontalAlignment.Left;
                                found2.VerticalAlignment = VerticalAlignment.Center;
                                container.Children.Add(found2);
                            }
                        }
                    }
                }
            }
        }
    }
}
