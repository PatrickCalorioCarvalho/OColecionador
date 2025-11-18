using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using OColecionadorBackEnd.Model;

namespace OColecionadorBackEnd.Data
{
    public class OColecionadorBackEndContext : DbContext
    {
        public OColecionadorBackEndContext(DbContextOptions<OColecionadorBackEndContext> options)
            : base(options)
        {
        }

        public DbSet<OColecionadorBackEnd.Model.Categoria> Categoria { get; set; } = default!;
        public DbSet<OColecionadorBackEnd.Model.Item> Item { get; set; } = default!;
        public DbSet<OColecionadorBackEnd.Model.Foto> Foto { get; set; } = default!;
    }
}
