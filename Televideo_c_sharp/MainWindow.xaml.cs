using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Net.Http;
using System.IO;
using System.Windows.Media;
using System.Globalization;

namespace Televideo;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    ScrollViewer viewer = new ScrollViewer();
    StackPanel container = new StackPanel();
    string filePath = Path.Combine(AppContext.BaseDirectory, "conf/programs.txt");
    private string[] programs;
    private struct channel
    {
        public string name;
        public string url;
    };
    private channel[] channels;
    public MainWindow()
    {
        try
        {
            InitializeComponent();
            FindChannels();
            viewer.VerticalScrollBarVisibility = ScrollBarVisibility.Visible;
            viewer.Content = container;
            window.Content = viewer;
            InsertProgramsToSearch();
        }
        catch (Exception ex)
        {
            MessageBox.Show(ex.ToString(), "ERRORE");
            throw;
        }
    }

    private async Task FindChannels()
    {
        string sURL = "https://guidatv.quotidiano.net/";
        string siteContent = await GetWebPage(sURL);
        if (string.IsNullOrEmpty(siteContent))
            return;
        Regex rx = new Regex("<section class=\"channel channel-thumbnail\".*?</section>", RegexOptions.Singleline);
        MatchCollection matches = rx.Matches(siteContent);
        Regex rx2 = new Regex("(?<=class=\"channel-name\">)(.*?)(?=</span>)", RegexOptions.IgnoreCase);
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

    private static readonly HttpClient http = new HttpClient();

    private async Task<string> GetWebPage(string url)
    {
        try
        {
            return await http.GetStringAsync(url);
        }
        catch
        {
            ShowErrorMessage("Errore di connessione a " + url);
            return "";
        }
    }

    private void ShowErrorMessage(string text)
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

    private void InsertProgramsToSearch()
    {
        int i = 0;
        AddTextBlock("Programmi da cercare", i++);

        try
        {
            string[] lines = File.ReadAllLines(Path.Combine(Environment.CurrentDirectory, filePath));
            foreach (string line in lines)
            {
                AddStackPanelWithTextBoxAndButton(line, i++);
            }
        }
        catch(FileNotFoundException)
        {
            
        }
        finally
        {
            AddStackPanelWithAddAndSearchButtons(i++);
        }
        
    }

    private void AddTextBlock(string text, int tag)
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

    private void AddStackPanelWithTextBoxAndButton(string line, int tag)
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
        tb.LostFocus += new RoutedEventHandler(TextBox_LostFocus);
        st1.Children.Add(tb);
        Button b = new Button();
        b.Content = "Rimuovi";
        b.Height = 30;
        b.Width = 100;
        b.Click += new RoutedEventHandler(RemoveButton_Click);
        st1.Tag = tag;
        st1.Children.Add(b);
        container.Children.Add(st1);
    }

    private void AddStackPanelWithAddAndSearchButtons(int tag)
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
        addButton.Click += new RoutedEventHandler(AddButton_Click);
        st2.Children.Add(addButton);
        Button searchButton = new Button();
        searchButton.Content = "Cerca programmi";
        searchButton.Height = 30;
        searchButton.Width = 200;
        searchButton.Click += new RoutedEventHandler(SearchButton_Click);
        st2.Children.Add(searchButton);
        st2.Tag = tag;
        container.Children.Add(st2);
    }

    private void TextBox_LostFocus(object sender, RoutedEventArgs e)
    {
        int index = (int)((StackPanel)((TextBox)sender).Parent).Tag;
        try
        {
            string[] lines = File.ReadAllLines(Path.Combine(Environment.CurrentDirectory, filePath));
            if (index > lines.Length)
            {
                string[] newLines = new string[lines.Length + 1];
                for (int i = 0; i < lines.Length; i++)
                {
                    newLines[i] = lines[i];
                }
                newLines[lines.Length] = ((TextBox)sender).Text;
                File.WriteAllLines(Path.Combine(Environment.CurrentDirectory, filePath), newLines);
            }
            else
            {
                lines[index - 1] = ((TextBox)sender).Text;
                File.WriteAllLines(Path.Combine(Environment.CurrentDirectory, filePath), lines);
            }
        }
        catch (FileNotFoundException)
        {
            string[] newLine = new string[] { ((TextBox)sender).Text };
            File.WriteAllLines(Path.Combine(Environment.CurrentDirectory, filePath), newLine);
        }
    }

    private void RemoveButton_Click(object sender, RoutedEventArgs e)
    {
        int index = (int)((StackPanel)((Button)sender).Parent).Tag;
        try
        {
            string[] lines = File.ReadAllLines(Path.Combine(Environment.CurrentDirectory, filePath));
            if (index <= lines.Length)
            {
                string[] newLines = new string[lines.Length - 1];
                int j = 0;
                for (int i = 0; i < lines.Length; i++)
                {
                    if (i != index - 1)
                        newLines[j++] = lines[i];
                }
                File.WriteAllLines(Path.Combine(Environment.CurrentDirectory, filePath), newLines);
            }
        }
        catch (FileNotFoundException)
        {
            
        }
        finally
        {
            container.Children.RemoveRange(0, container.Children.Count);
            InsertProgramsToSearch();
        }
    }

    private void AddButton_Click(object sender, RoutedEventArgs e)
    {
        int index = (int)((StackPanel)((Button)sender).Parent).Tag;
        container.Children.RemoveRange(index, container.Children.Count);

        AddStackPanelWithTextBoxAndButton("", index++);
        AddStackPanelWithAddAndSearchButtons(index++);
    }

    private async void SearchButton_Click (object sender, RoutedEventArgs e)
    {
        LoadProgramsToSearch();
        if (programs == null)
            return;
        int index = (int)((StackPanel)((Button)sender).Parent).Tag;
        if (container.Children.Count > index)
            container.Children.RemoveRange(++index, container.Children.Count);
        await FindPrograms();
    }

    private void LoadProgramsToSearch()
    {
        try
        {
            string[] lines = File.ReadAllLines(Path.Combine(Environment.CurrentDirectory, filePath));
            programs = new string[lines.Length];
            int i = 0;
            foreach (string line in lines)
                programs[i++] = line;
        }
        catch (FileNotFoundException)
        {
            ShowErrorMessage("Nessun programma inserito");
        }
        
    }

    private async Task FindPrograms()
    {
        Console.WriteLine("Start at " + DateTime.Now.ToString("HH:mm:ss"));
        DateTime today = DateTime.Today;
        var tasks = new List<Task<string>>();
        int metaIndex = 0;
        (int, string)[] metadati = new (int, string)[channels.Length * 7 + 1];
        for (int j = 0; j < channels.Length; j++) {
            for (int d = 0; d < 7; d++)
            {
                DateTime day = today.AddDays(d);
                string dayString = day.ToString("dd-MM-yyyy");
                tasks.Add(GetWebPage(channels[j].url + dayString));
                metadati[metaIndex++] = (j, dayString);
            }
        }
        string[] results = await Task.WhenAll(tasks);
        for (int i = 0; i < results.Length; i++)
        {
            string dayString = metadati[i].Item2;
            int j = metadati[i].Item1;
            string siteContent = results[i];
            if (siteContent.Equals("")) {
                return;
            }
            int startIndex = siteContent.IndexOf("<section id=\"faqs\">");
            if (startIndex < 0)
                continue;
            siteContent = siteContent.Substring(startIndex);
            int endIndex = siteContent.IndexOf("</li></ul>");
            siteContent = siteContent.Substring(0, endIndex + 5);
            Regex rx = new Regex("(?<=<li>)(.*?)(?=</li>)", RegexOptions.IgnoreCase);
            MatchCollection matches = rx.Matches(siteContent);
            string lastTimeString = matches[matches.Count - 1].Value.Substring(0, 5);
            DateTime lastTime = DateTime.ParseExact(lastTimeString + ":00", "HH:mm:ss", CultureInfo.InvariantCulture);
            DateTime firstTime = DateTime.ParseExact("06:00:00", "HH:mm:ss", CultureInfo.InvariantCulture);
            int elementsCount = matches.Count;
            if (firstTime.Equals(lastTime))
                elementsCount -= 1;

            for (int ctr = 0; ctr < elementsCount; ctr++)
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
                        string timeString = matches[ctr].Value.Substring(0, 5);
                        DateTime time = DateTime.ParseExact(timeString + ":00", "HH:mm:ss", CultureInfo.InvariantCulture);
                        if (time.CompareTo(DateTime.ParseExact("00:00:00", "HH:mm:ss", CultureInfo.InvariantCulture)) >= 0
                            && time.CompareTo(DateTime.ParseExact("06:00:00", "HH:mm:ss", CultureInfo.InvariantCulture)) < 0)
                            found2.Text = DateTime.ParseExact(dayString, "dd-MM-yyyy", CultureInfo.InvariantCulture).AddDays(1).ToString("dd-MM-yyyy") + " " + channels[j].name + " " + matches[ctr].Value;
                        else
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
        TextBlock end = new TextBlock();
        end.Text = "Ricerca completata";
        end.Height = 30;
        end.FontSize = 20;
        end.HorizontalAlignment = HorizontalAlignment.Center;
        end.VerticalAlignment = VerticalAlignment.Center;
        end.Background = new SolidColorBrush(Colors.White);
        end.Foreground = new SolidColorBrush(Colors.Green);
        container.Children.Add(end);
        Console.WriteLine("End at " + DateTime.Now.ToString("HH:mm:ss"));
    }
}