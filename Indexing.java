package myDemo;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.core.LowerCaseFilterFactory;
import org.apache.lucene.analysis.core.StopFilterFactory;
import org.apache.lucene.analysis.custom.CustomAnalyzer;
import org.apache.lucene.analysis.en.PorterStemFilterFactory;
import org.apache.lucene.analysis.standard.StandardTokenizerFactory;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexReaderContext;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.PostingsEnum;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexableField;
import org.apache.lucene.search.DocIdSetIterator;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.index.Term;
import org.apache.lucene.index.Terms;
import org.apache.lucene.index.TermsEnum;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.BytesRef;
import org.jsoup.Jsoup;


public class Indexing {
	
	static LuceneIndexConfig config = new LuceneIndexConfig();
	
	//String indexPath = "C:\\Personal\\OVGU\\WiSe2020\\IR\\eclipse\\Lucene\\indexedFiles2";
	private static int docId = 0;


	public static void main(String[] args) throws IOException
	{
		//Input folder
		String docsPath = "C:\\Personal\\OVGU\\WiSe2020\\IR\\P07\\chatbot_doc2vec\\output";

		//Output folder
		String indexPath = config.getIndexDir();

		final Path docDir = Paths.get(docsPath);

		//Paths.get("/path/to/config/dir")
		Analyzer analyzer = CustomAnalyzer.builder()
				.withTokenizer(StandardTokenizerFactory.class)
				.addTokenFilter(LowerCaseFilterFactory.class)
				.addTokenFilter(StopFilterFactory.class)
				.addTokenFilter(PorterStemFilterFactory.class)
				.build();

		//org.apache.lucene.store.Directory instance
		Directory indexedFilesdir = FSDirectory.open( Paths.get(indexPath) );


		//IndexWriter Configuration
		IndexWriterConfig iwc = new IndexWriterConfig(analyzer);
		iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);

		//IndexWriter writes new index files to the directory
		IndexWriter writer = new IndexWriter(indexedFilesdir, iwc);

		int originalNumDocs = writer.numDocs();

		System.out.println("");
		System.out.println("************************");
		System.out.println((originalNumDocs) + " previous documents.");
		System.out.println("************************");

		//Its recursive method to iterate all files and directories
		indexDocs(writer, docDir);

		//===================================================
		//Displaying number of documents added
		//===================================================
		int newNumDocs = writer.numDocs();
		System.out.println("");
		System.out.println("************************");
		System.out.println((newNumDocs - originalNumDocs) + " documents added.");
		System.out.println("************************");

		//===================================================
		//closeIndex to complete index creation    
		//===================================================
		writer.close();


	}
	
	private static void writeINexcel(ArrayList<String> list, FileWriter csvwriter, StringBuilder sb) throws IOException {
	
		if(docId==0) {
			sb.append("id");
			sb.append("\t");
			sb.append("docPath");
			sb.append("\t");
			sb.append("docContent");
			sb.append('\n');
		}

		sb.append(docId);
		sb.append("\t");
		sb.append(list);
		sb.append('\n');


		System.out.println(sb.toString());
		csvwriter.write(sb.toString());

		System.out.println("done!");

	}

	private static void indexDocs(IndexWriter writer, Path path) throws IOException {	

		//Directory?
		if (Files.isDirectory(path)) 
		{
			//Iterate directory
			Files.walkFileTree(path, new SimpleFileVisitor<Path>()
			{
				@Override
				public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException 
				{
					try
					{
						if (file.toString().toLowerCase().endsWith(".txt")) 
						{
							//Index this text file
							indexTextDoc(writer, file, attrs.lastModifiedTime().toString());
							
						} 
						/*
						 * else if (file.toString().toLowerCase().endsWith(".htm") ||
						 * file.toString().toLowerCase().endsWith(".html") ) { //Index this html file
						 * indexHtmlDoc(writer, file, attrs.lastModifiedTime().toString());
						 * termVectors(); }
						 */
						else {
							System.out.println("Skipped " + file);
						}

					} 
					catch (IOException ioe) {
						ioe.printStackTrace();
					}
					return FileVisitResult.CONTINUE;
				}
			});
		} 
		else if (path.toString().toLowerCase().endsWith(".txt")) 
		{
			//Index this text file
			indexTextDoc(writer, path, Files.getLastModifiedTime(path).toString());
		}
		else if (path.toString().toLowerCase().endsWith(".htm") || path.toString().toLowerCase().endsWith(".html")) 
		{
			//Index this html file
			indexHtmlDoc(writer, path, Files.getLastModifiedTime(path).toString());
		}
		else {
			System.out.println("Skipped: " + path);
		}
	}

	public static void indexHtmlDoc(IndexWriter writer, Path file, String lastModified) throws IOException 
	{

		Document doc = new Document();

		//Create lucene Document
		try (InputStream stream = Files.newInputStream(file)) 
		{
			org.jsoup.nodes.Document htmldoc = Jsoup.parse(new File(file.toString()),"utf-8");

			doc.add(new StringField("path", file.toString(), Field.Store.YES));
			doc.add(new TextField("title", htmldoc.title(), Field.Store.YES));
			doc.add(new TextField("modified", lastModified, Field.Store.YES));
			doc.add(new TextField("contents", htmldoc.body().text(), Store.YES));

			FieldType myFieldType = new FieldType(TextField.TYPE_STORED);
			myFieldType.setStoreTermVectors(true);
			myFieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS);
			myFieldType.setTokenized(true);
			myFieldType.setStored(true);
			myFieldType.setStoreTermVectors(true);  //Store Term Vectors
			myFieldType.freeze();
			StoredField termV = new StoredField("termV",htmldoc.body().text(),myFieldType);
			doc.add(termV);

			//Updates a document by first deleting the document(s) 
			writer.updateDocument(new Term("path", file.toString()), doc);

			System.out.println("Added: " + doc.get("path"));

		} 
		catch (Exception e) {
			System.out.println("Could not add: " + doc.get("path"));
		} 
	}


	public static void indexTextDoc(IndexWriter writer, Path file, String lastModified) throws IOException 
	{
		//Create lucene Document
		Document doc = new Document();
		try (InputStream stream = Files.newInputStream(file)) 
		{

			doc.add(new StringField("path", file.toString(), Field.Store.YES));
			doc.add(new TextField("modified", lastModified, Field.Store.YES));
			doc.add(new TextField("contents", new String(Files.readAllBytes(file)), Store.YES));


			FieldType myFieldType = new FieldType(TextField.TYPE_STORED);
			myFieldType.setStoreTermVectors(true);
			myFieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS);
			myFieldType.setTokenized(true);
			myFieldType.setStored(true);
			myFieldType.setStoreTermVectors(true);  //Store Term Vectors
			myFieldType.freeze();
			StoredField termV = new StoredField("termV",new String(Files.readAllBytes(file)),myFieldType);
			doc.add(termV);


			//Updates a document by first deleting the document(s) 
			writer.updateDocument(new Term("path", file.toString()), doc);

			//Field.TermVector.YES

			System.out.println("Added: " + doc.get("path"));

		} 
		catch (Exception e) {
			System.out.println("Could not add: " + doc.get("path"));
		} 
	}
}

