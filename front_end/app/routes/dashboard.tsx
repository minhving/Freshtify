import React from "react";

function Dashboard() {
  return (
    <body className="">
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Produce Section</h1>
        {/* // Placeholder for last analyzed  time */}
        <p>Last analyzed: Today, 2:45PM</p>
        {/* Grid for total products, low stock, medium stock, high stock */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-5">
          {/* Total Produts */}
          <div className="bg-secondary rounded-2xl px-4 py-4">
            <h4 className="text-primary font-medium">Total Products</h4>
            <p className="text-primary text-3xl font-semibold">48</p>
          </div>
          <div className="bg-lowStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-lowStock-text font-medium">Low Stocks</h4>
            <p className="text-primary text-3xl font-semibold">5</p>
          </div>
          <div className="bg-mediumStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-mediumStock-text font-medium">Medium Stock</h4>
            <p className="text-primary text-3xl font-semibold">12</p>
          </div>
          <div className="bg-highStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-highStock-text font-medium">High Stock</h4>
            <p className="text-primary text-3xl font-semibold">33</p>
          </div>
        </div>
      </div>

      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 mb-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Product Overview</h1>
        {/* Chart Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-secondary rounded-2xl h-96 mt-5">
            {/* Placeholder for Chart */}
            <p className="text-primary text-center pt-40">
              [Chart Placeholder]
            </p>
          </div>
          <div className="bg-secondary rounded-2xl h-96 mt-5">
            {/* Placeholder for Chart */}
            <p className="text-primary text-center pt-40">
              [Chart Placeholder]
            </p>
          </div>
        </div>
        {/* Table Section */}
        <div className="rounded-2xl mt-5 p-4 ">
          <table className="table-auto ">
            <thead className="">
              <tr className="bg-secondary text-primary rounded-2xl">
                <th>Product</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Status</th>
                <th>Last updated</th>
              </tr>
              {mockProducts.map((product) => (
                <tr key={product.id} className="text-center">
                  <td>{product.product}</td>
                  <td>{product.category}</td>
                  <td>{product.stock}</td>
                  <td>{product.status}</td>
                  <td>{product.updatedAt}</td>
                </tr>
              ))}
            </thead>
          </table>
        </div>
      </div>
    </body>
  );
}

export default Dashboard;

{
  /* shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] */
}

export const mockProducts = [
  {
    id: 1,
    product: "Banana",
    category: "Fruit",
    stock: "80%",
    status: "High",
    updatedAt: "Today, 2:45 PM",
  },
  {
    id: 2,
    product: "Broccoli",
    category: "Vegetable",
    stock: "20%",
    status: "Low",
    updatedAt: "Today, 2:42 PM",
  },
  {
    id: 3,
    product: "Avocado",
    category: "Fruit",
    stock: "60%",
    status: "Medium",
    updatedAt: "Today, 2:40 PM",
  },
  {
    id: 4,
    product: "Tomato",
    category: "Vegetable",
    stock: "95%",
    status: "High",
    updatedAt: "Today, 2:38 PM",
  },
  {
    id: 5,
    product: "Onion",
    category: "Vegetable",
    stock: "45%",
    status: "Medium",
    updatedAt: "Today, 2:35 PM",
  },
  {
    id: 6,
    product: "Apple",
    category: "Fruit",
    stock: "10%",
    status: "Low",
    updatedAt: "Today, 2:30 PM",
  },
  {
    id: 7,
    product: "Carrot",
    category: "Vegetable",
    stock: "85%",
    status: "High",
    updatedAt: "Today, 2:25 PM",
  },
];
