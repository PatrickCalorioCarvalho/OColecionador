namespace OColecionadorBackEnd.Model
{
    public class Foto
    {
        public int Id { get; set; }
        public required string Caminho { get; set; }
        public int ItemId { get; set; }
        public Item? Item { get; set; }
    }
}
